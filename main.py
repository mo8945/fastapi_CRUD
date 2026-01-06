from typing import List
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


app = FastAPI()

app.mount("/public", StaticFiles(directory="public"), name="public")
templates = Jinja2Templates(directory="views")

class Car(BaseModel):
    seq: int
    name: str
    price: int
    company: str
    year: int

car_list: List[Car] = [
    Car(seq=1001, name="SONATA", price=2000, company="HYUNDAI", year=2020),
    Car(seq=1002, name="K7", price=3700, company="KIA", year=2018),
    Car(seq=1003, name="SM6", price=1800, company="르노", year=2017),
    Car(seq=1004, name="G80", price=5000, company="제네시스", year=2017),
]

sequence = max(c.seq for c in car_list) + 1

@app.get("/test", response_class=HTMLResponse)
def test(request: Request):
    html = f"GET - /test/<br/>{request.url.path}"
    return HTMLResponse(content=html, status_code=200)

@app.get("/car/list", response_class=HTMLResponse)
def car_list_page(request: Request):
    return templates.TemplateResponse(
        "car/list.html",
        {"request":request, "car_list":car_list}
    )

@app.get("/car/modify/{seq}", response_class=HTMLResponse)
def car_modify_page(request: Request, seq: int):
    car = next((c for c in car_list if c.seq == seq), None)
    if car is None:
        return RedirectResponse(url="/car/list", status_code=303)
    
    return templates.TemplateResponse(
        "car/modify.html",
        {"request": request, "car": car},
    )

@app.post("/car/input")
def car_input(
    name: str = Form(...),
    price: int = Form(...),
    company: str = Form(...),
    year: int = Form(...),
):
    global sequence
    new_car = Car(seq=sequence, name=name, price=price, company=company, year=year)
    car_list.append(new_car)
    sequence += 1
    return RedirectResponse(url="/car/list", status_code=303)

@app.post("/car/modify/{seq}")
def car_modify(
    seq: int,
    name: str = Form(...),
    price: int = Form(...),
    company: str = Form(...),
    year: int = Form(...),
):
    idx = next((i for i, c in enumerate(car_list) if c.seq == seq), -1)
    if idx != -1:
        car_list[idx] = Car(seq=seq, name=name, price=price, company=company, year=year)
        return RedirectResponse(url="/car/list", status_code=303)
    return RedirectResponse(url="/car/list", status_code=303)

@app.get("/car/delete/{seq}")
def car_delete(seq: int):
    idx = next((i for i, c in enumerate(car_list) if c.seq == seq), -1)
    if idx != -1:
        car_list.pop(idx)
    return RedirectResponse(url="/car/list", status_code=303)

@app.get("/car/api/list")
def car_api_list():
    return jsonable_encoder(car_list)