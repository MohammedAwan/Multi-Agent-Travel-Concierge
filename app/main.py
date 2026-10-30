from dotenv import load_dotenv
load_dotenv()
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.core.database import db_pool, init_db, DATABASE_URL
from app.core.security import hash_password, verify_password, create_access_token, get_current_user
from app.schemas.auth import UserRegister, UserLogin, TokenResponse
from app.schemas.request import TravelFormRequest, ChatFollowUpRequest
from app.graph.workflow import create_travel_graph, builder
from psycopg_pool import AsyncConnectionPool

from fastapi import APIRouter, Depends
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.security import get_current_user

from app.graph.nodes import llm
import traceback
# Global reference for the compiled graph
travel_graph = None

# 2. Define the connection pool
DATABASE_URL = os.getenv("DATABASE_URL")

travel_graph = None

# 2. Define the connection pool BEFORE lifespan
db_pool = AsyncConnectionPool(
    conninfo=DATABASE_URL,
    max_size=10,
    min_size=1,
    max_idle=30.0,
    check=AsyncConnectionPool.check_connection,
    open=False  # Stays closed until lifespan opens it
)

travel_graph = None

# 3. Define lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    global travel_graph

    # Open the shared pool and wait until connections are ready
    await db_pool.open()
    await db_pool.wait()
    
    # Run user/app DB table initialization
    await init_db()

    # Pass an active connection context to AsyncPostgresSaver
    async with db_pool.connection() as conn:
        checkpointer = AsyncPostgresSaver(conn)
        await checkpointer.setup()  # Run LangGraph checkpoint migrations
        travel_graph = create_travel_graph(checkpointer)

    yield

    # Clean shutdown
    await db_pool.close()
app = FastAPI(title="AI Travel Planner API", version="2.0.0", lifespan=lifespan)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files & Jinja2 templates (Preserving your existing frontend)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Entry page: always loads the authentication view first."""
    return templates.TemplateResponse(request=request, name="auth.html")

@app.get("/planner", response_class=HTMLResponse)
async def planner_home(request: Request):
    """The protected travel planner UI."""
    return templates.TemplateResponse(request=request, name="index.html")
# ----------------- AUTHENTICATION ROUTES ----------------- #

@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    hashed_pwd = hash_password(user_data.password)
    try:
        async with db_pool.connection() as conn:
            result = await conn.execute(
                "INSERT INTO users (email, hashed_password, full_name) VALUES (%s, %s, %s) RETURNING id;",
                (user_data.email, hashed_pwd, user_data.full_name)
            )
            user = await result.fetchone()
            return {"message": "User registered successfully", "user_id": user["id"]}
    except Exception as exc:
        if "unique constraint" in str(exc).lower():
            raise HTTPException(status_code=400, detail="Email already registered.")
        raise HTTPException(status_code=500, detail="Database registration failed.")

@app.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    async with db_pool.connection() as conn:
        result = await conn.execute(
            "SELECT id, hashed_password FROM users WHERE email = %s;",
            (credentials.email,)
        )
        user = await result.fetchone() # returns tuple
        # converting it into dict
        user_dict = {
            'id' : user[0],
            'hashed_password': user[1]
        }
        user = user_dict
        
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
        
    access_token = create_access_token(data={"sub": str(user["id"])})
    return {"access_token": access_token, "token_type": "bearer"}

# ----------------- PROTECTED ITINERARY GENERATION ----------------- #

@app.post("/generate_itinerary")
async def generate_itinerary(
    payload: TravelFormRequest,
    current_user_id: int = Depends(get_current_user)
):
    try:
        session_id = payload.session_id or f"sess_{current_user_id}"
        config = {"configurable": {"thread_id": f"user_{current_user_id}_{session_id}"}}

        initial_state = {
            "messages": [],
            "destination": payload.destination,
            "duration": payload.duration,
            "travel_dates": payload.travel_dates,
            "accommodation": payload.accommodation,
            "budget": payload.budget,
            "interests": payload.interests,
            "pace": payload.pace,
            "dietary_restrictions": payload.dietary_restrictions,
            "special_requests": payload.special_requests,
            "final_itinerary": None
        }

        async with db_pool.connection() as conn:
            checkpointer = AsyncPostgresSaver(conn)
            await checkpointer.setup()
            graph = builder.compile(checkpointer=checkpointer)
            result = await graph.ainvoke(initial_state, config=config)

        output_data = result.get("final_itinerary")
        if not output_data and result.get("messages"):
            output_data = result["messages"][-1].content

        # Handle both raw Markdown string and Pydantic objects safely
        if isinstance(output_data, str):
            itinerary_md = output_data
            structured_data = {}
        elif hasattr(output_data, "to_markdown_text"):
            itinerary_md = output_data.to_markdown_text()
            structured_data = output_data.model_dump() if hasattr(output_data, "model_dump") else {}
        else:
            itinerary_md = str(output_data)
            structured_data = {}

        return JSONResponse(content={
            "itinerary": itinerary_md,
            "structured_data": structured_data,
            "session_id": payload.session_id
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to generate itinerary. Please try again."}
        )
    
@app.post("/chat_refine")
async def chat_refine(
    payload: ChatFollowUpRequest,
    current_user_id: int = Depends(get_current_user)
):
    try:
        # Prompt the model directly with conversational context to avoid tool-schema JSON crashes
        system_prompt = SystemMessage(content=(
            "You are an expert travel concierge. The user wants to adjust their EXISTING travel itinerary.\n"
            "CRITICAL INSTRUCTIONS:\n"
            "- Modify ONLY the requested items in the existing itinerary provided below.\n"
            "- Retain the exact same destination, dates, and overall structure unless explicitly told to change them.\n"
            "- Format your response into TWO sections separated strictly by '---ITINERARY---':\n"
            "  1. A concise summary (1–2 sentences) explaining what was modified.\n"
            "  ---ITINERARY---\n"
            "  2. The COMPLETE, revised full itinerary in Markdown format."
        ))

        user_content = (
            f"### CURRENT ITINERARY:\n{payload.current_itinerary}\n\n"
            f"### REQUESTED ADJUSTMENT:\n{payload.message}"
        )
        user_prompt = HumanMessage(content=user_content)

        ai_response = await llm.ainvoke([system_prompt, user_prompt])
        full_text = ai_response.content

        # Split conversational reply from the complete itinerary
        if "---ITINERARY---" in full_text:
            chat_reply, updated_itinerary = full_text.split("---ITINERARY---", 1)
        else:
            # Fallback if delimiter was omitted
            chat_reply = "I've updated your itinerary on the left with your changes!"
            updated_itinerary = full_text

        return JSONResponse(content={
            "reply": chat_reply.strip(),
            "updated_itinerary": updated_itinerary.strip(),
            "session_id": payload.session_id
        })

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Error updating itinerary: {str(e)}"}
        )