# TODO List API

A simple TODO list API to demonstrate [Fractional](https://begriffs.com/posts/2018-03-20-user-defined-order.html#approach-3-true-fractions) and [Lexorank](https://yasoob.me/posts/how-to-efficiently-reorder-or-rerank-items-in-database/#approach-3-order-items-using-lexorank) sorting solutions for user defined order

Live demo available [here](https://todo.labtoast.com/docs)

Built with FastAPI

## Database

### Model

**id**: Integer. Primary key
<br/>
**task_detail**: String. Task content
<br/>
**numerator**: Integer. Used for Fractional
<br/>
**denominator**: Integer. Used for Fractional
<br/>
**order**: Integer. Used for Fractional. Used for sorting
<br/>
**rank**: String. Used for Lexorank. Used for sorting

### Sample

| id  | task_detail | numerator | denominator | order | rank |
| :-: | :---------: | :-------: | :---------: | :---: | :--: |
|  0  |  Get lunch  |     1     |      1      |   1   |  i   |

## Usage

### Routes

- GET /tasks
  - Get all tasks, ordered by the order column(Fractional)
- GET /tasks/rank
  - Get all tasks, ordered by the rank column(Lexorank)
- POST /tasks
  - Add a new task to the end of the list
- PUT /tasks/{task_id}
  - Get a task by its id and update its task_detail
- PUT /tasks/move/{task_id}
  - Get a task by its id and move it
  - Use only next_task_id if moving to the start
  - Use only prev_task_id if moving to the end
  - Use both if moving in-between tasks
  - Updates a task's numerator, denominator, order, and rank
- DELETE /tasks/{task_id}
  - Get a task by its id and delete it

_Check the [docs](https://todo.labtoast.com/docs) for the body schemas of each route_

## Project Setup

### Install requirements

```sh
pip install -r requirements.txt
```

### Run migrations

```sh
alembic upgrade head
```

### Run ASGI Server

```sh
fastapi dev app/main.py
```

### Run Unit Tests

```sh
pytest
```

## Project Setup With Docker

### Build Docker Image

```sh
docker build -t todoapi .
```

### Run Docker Image

```sh
docker run -p 8080:80 todoapi:latest
```

## Documentation

Documentation is available at /docs

If running locally: http://127.0.0.1:8000/docs
<br/>
If running locally with docker: http://localhost:8080/docs
