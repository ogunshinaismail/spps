from typing import Any
from fastapi import FastAPI, Body, Response
from fastapi.middleware.cors import CORSMiddleware
import pickle as pl
import pandas as pd
from openai import OpenAI
import numpy as np
import os
import asyncio as aio
from db import Users, execute, Courses, Student_Grade, _db
from pydantic import BaseModel
from sqlalchemy import select, insert
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import re

load_dotenv()

# Set random seed for reproducibility
np.random.seed(100)

app = FastAPI()
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://spps-v0.vercel.app",
    "https://spps-server.vercel.app",
    "https://sppsserver-production.up.railway.app",
    "https://fvnk7h-8000.csb.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set the API key (preferably from environment variable)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY"),
)

@app.get("/")
async def root():
    return {"message": "Hello World from SPPS Server!"}

def clean_recommendation(text: str) -> str:
    # Remove all asterisks
    text = text.replace('*', '')
    # Ensure a blank line before each numbered list item (for Markdown readability)
    text = re.sub(r'(\n)(\d+\.)', r'\n\n\2', text)
    # Replace escaped \n with real line breaks (if needed)
    text = text.replace('\\n', '\n')
    # Optionally, strip leading/trailing whitespace
    return text.strip()

class PredictionModel(BaseModel):
    score: list[float]
    course_unit: list[int]
    gpa: float

async def predict_gpa(data):
    # print(data)
    if not data:
        return {"error": "No data provided"}
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        MODEL_PATH = os.path.join(BASE_DIR, 'api/results.pkl')
        SCALER_PATH = os.path.join(BASE_DIR, 'api/scaler.pkl')
        with open(MODEL_PATH, 'rb') as f:
            lr = pl.load(f)
            scaler = open(SCALER_PATH, 'rb')
            scaler = pl.load(scaler)
            X = np.array(data)[ : 2].reshape(1, -1)
            X = pd.DataFrame(X, columns=['course_unit', 'wgp'])
            X = scaler.transform(X)
            predict_gpa = lr.predict(X)
            # print("Predicted GPA", round(predict_gpa[0], 2))
            # print(round(data[-1 : ], 2))

            gpa_prompt = [
                dict(role="system", content="You are a helpful and encouraging school teacher and your task is give recommendations based on a students's gpa. " \
                "Please be short and concise. Please also make sure to use indentions where necessary like when listing steps"),
                
                dict(role="user", content=f"Given the current gpa {round(data[-1 : ][0], 2)} and predicted gpa {round(predict_gpa[0], 2)}, please give me recommendations to know how to improve my gpa or to keep the good work"),
            ]
            # print("GPA Prompt", gpa_prompt)

            try:
                response = client.chat.completions.create(
                model="deepseek/deepseek-r1:free",  # or "gpt-4" if you have access
                messages=gpa_prompt,
                )
                # Print the response
                # print(response.choices[0].message.content)

                if not response.choices or not response.choices[0].message.content:
                    # print("Response not sent")
                    return {"error": "No response from OpenAI API."}
                else:
                    # print("Response sent")
                    return {"current_gpa": round(data[-1 : ][0], 2), "predicted_gpa": round(predict_gpa[0], 2), "response": response.choices[0].message.content}
            except Exception as e:
                print(f"Error: {e}")
                return {}
            # print("Response from OpenAI API:", response)

    except Exception as e:
        print(f"Error: {e}")
        return {"error": "An error occurred while processing the data."}
    
class PredictUserModel(BaseModel):
    user_id: str

@app.post("/api/predict")
async def predict(user: PredictUserModel):
    # return await aio.to_thread(predict_gpa, data)    
    # print(user.user_id)
    result = None
    weight: list[float] | float = []
    course_unit: list[int] | int = []
    wgp = []
    select_result = select(Student_Grade.c.course_unit, Student_Grade.c.weight).where(Student_Grade.c.student_id == user.user_id)

    with _db.connect() as conn:
        result = conn.execute(select_result)
    results = result.fetchall()

    if len(results) == 0:
        return {}
    # print("Results", results)
    for r in results:
        course_unit.append(r[0])
        weight.append(round(r[1], 2))
    # print("Course Unit", course_unit, "Weight", weight)
    course_unit = np.array(course_unit)
    weight = np.array(weight)

    # wgp = [course_unit[i] * weight[i] for i in range(len(course_unit))]
    wgp = weight * course_unit
    # print("WGPA", wgp)
    course_unit = course_unit.sum()
    wgp = wgp.sum()

    # print("Course Unit", course_unit, "Weight", wgp, "GPA", round(wgp/course_unit, 2))
    return await predict_gpa(
        [
            # all_scores,
            course_unit,
            # weight,
            wgp,
            # round(np.random.random() * 100),  # attendance
            # round(np.random.random() * 12),   # study time
            min(round(wgp / course_unit, 2), 4.00), # GPA
        ]
    )

class LoginModel(BaseModel):
    user_id: str
    password: int | str

@app.post("/api/login")
async def login(data: LoginModel, resp: Response):
    # print(data)
    if not data.user_id or not data.password:
        return {"error": "Matric number and password are required."}

    query = select(Users).where(Users.c.user_id == data.user_id.lower())
    result = None
    with _db.connect() as conn:
        result = conn.execute(query)
        conn.commit()
    
    if result.rowcount == 0:
        return {"error": "Invalid matric number or password."}

    query_data = result.mappings().first()
    # print(query_data)

    if query_data.password != data.password:
        return {"error": "Invalid matric number or password."}
    else:
        # expires = datetime.now(timezone.utc) + timedelta(days=1)
        # resp.set_cookie(
        #     key="user_data",
        #     value=f"{query_data}",
        #     httponly=False,
        #     samesite=None,
        #     expires=expires
        # )
        return query_data
    
    
@app.get("/api/courses/{user_id}")
async def get_courses(user_id: str):
    if(not user_id):
        return {"error": "User ID is required."}
    
    query = select(Courses). where(Courses.c.lecturer_id == user_id)
    result = None
    
    with _db.connect() as conn:
        result = conn.execute(query)
        conn.commit()

    courses = result.mappings().all()

    if not courses:
        return {"courses": []}

    return {"courses": [dict(course) for course in courses]}


class ResultArrayModel(BaseModel):
    course_code: str
    lecturer_id: str
    student_id: str
    semester: str
    session: str
    course_unit: int
    ca_score: int
    exam_score: int
    total_score: int
    # percentage: float
    weight: float
    letter_grade: str

class ResultModel(BaseModel):
    results: list[ResultArrayModel]

@app.post("/api/save/result")
async def save_result(data: ResultModel):
    results = data.results
    # print(len(results))
    # print(results)
    try:
        result = None
        with _db.connect() as conn:
            result = conn.execute(insert(Student_Grade), [dict(result) for result in results])
            conn.commit()
        if not result:
            return {"success": False}
    except Exception as e:
        print("Error occured while inserting results", e)
    # for result in results:

    return {"success": True}

# Port configuration - run the server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,  # Change this to your desired port
        reload=True,
        log_level="info"
    )
