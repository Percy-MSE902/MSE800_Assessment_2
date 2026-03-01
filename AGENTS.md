# AGENTS.md - Agentic Coding Guidelines

This document provides guidelines for agents working on this codebase.

## Project Overview

This is a full-stack hotel housekeeping management system:
- **Backend**: FastAPI + SQLAlchemy + Pydantic + MySQL
- **Frontend**: Vue 3 + TypeScript + Element Plus + Pinia + vue-router

## Build Commands

### Frontend
```bash
cd frontend
npm install
npm run dev      # Development server
npm run build    # Build for production
npm run preview  # Preview production build
```

### Backend
```bash
cd backend/src
pip install -r requirements.txt
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
Note: Backend uses MySQL. Ensure MySQL is running and configured in `database.py`.

## Code Style Guidelines

### Python Backend

#### Imports
Standard library first, then third-party, then local. Use absolute imports:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.user import UserModel
from core.dependencies import get_current_user
from schemas.user import UserSchema
from cruds.CRUDBase import CRUDBase
```

#### Naming
- **Classes**: PascalCase (e.g., `UserModel`)
- **Functions/variables**: snake_case (e.g., `get_user`)
- **Constants**: UPPER_SNAKE_CASE

#### Type Hints
Always use type hints. Use `Optional[X]` instead of `X | None`:
```python
def get_user(user_id: int, db: Session = Depends(get_db)) -> Optional[UserModel]:
    ...
```

#### SQLAlchemy Models
Use `Mapped` and `mapped_column`. Define `__tablename__` explicitly. Use soft deletes:
```python
class UserModel(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
```

#### Pydantic Schemas
Use `BaseModel` with `Field`. Separate schemas for create, update, and response:
```python
class UserSchema(BaseModel):
    id: Optional[int] = None
    full_name: Optional[str] = Field(None, max_length=100)
    class Config:
        from_attributes = True
```

#### Error Handling
Use `HTTPException` with meaningful messages:
```python
if not db_obj:
    raise HTTPException(status_code=404, detail='Item not found')
```

#### API Routes
Use FastAPI routers with prefixes and tags. Separate public and protected routes:
```python
router = APIRouter(prefix='/api/user', tags=['user'])
public_router = APIRouter(prefix='/api/user', tags=['user'])
```

### Vue 3 Frontend

#### Script Setup
Use `<script setup lang="ts">` with Composition API:
```vue
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
</script>
```

#### TypeScript
Define proper types for props and reactive state. Use strict mode:
```typescript
interface LoginForm {
  username: string
  password: string
}
const loginForm = ref<LoginForm>({ username: '', password: '' })
```

#### Component Organization
Order: `<script setup>`, `<template>`, `<style scoped>`. Use `@` alias for imports.

#### Naming
Components: PascalCase (e.g., `UserList.vue`). Props: camelCase.

#### Vue Router
Use lazy loading for routes:
```typescript
const routes = [
  { path: '/', component: () => import('@/views/Dashboard.vue') }
]
```

#### State Management (Pinia)
Use composition API style stores:
```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  async function login(username: string, password: string) { ... }
  return { user, login }
})
```

## Database

Uses MySQL; models in `backend/src/models/`. Use soft deletes (`is_deleted = 1`) instead of hard deletes. Follow CRUDBase patterns.

## Common Patterns

### Adding a New API Resource
1. Create model in `backend/src/models/`
2. Create schema in `backend/src/schemas/`
3. Create CRUD in `backend/src/cruds/`
4. Create service in `backend/src/services/` (optional)
5. Create API in `backend/src/apis/`

### Adding a New Frontend View
1. Create Vue component in `frontend/src/views/`
2. Add route in router configuration
3. Use existing API services or create new ones in `frontend/src/api/`

## Testing

No test framework currently configured. When adding tests:
- Backend: Use `pytest` with `pytest-asyncio`
- Frontend: Use `vitest` or `jest`

Run a single test:
```bash
pytest tests/test_file.py::test_function_name -v
```
