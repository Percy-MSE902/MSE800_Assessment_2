# Vue 开发常见问题记录

## Element Plus DatePicker v-model 问题

### 问题描述
在 Vue 3 中使用 Element Plus 的 `el-date-picker` 组件时，不能直接在 `v-model` 中使用数组字面量 `[filters.start_date, filters.end_date]`。

**错误写法:**
```vue
<el-date-picker
  v-model="[filters.start_date, filters.end_date]"
  type="daterange"
/>
```

**报错:**
```
v-model value must be a valid JavaScript member expression
```

### 解决方案
使用一个独立的 ref 变量来绑定日期范围，然后通过 `@change` 事件处理程序来更新 filters 对象。

**正确写法:**
```vue
<script setup>
const filters = ref({
  start_date: '',
  end_date: ''
})

const dateRange = ref<[string, string] | null>(null)

const handleDateRangeChange = (val: [string, string] | null) => {
  if (val) {
    filters.value.start_date = val[0]
    filters.value.end_date = val[1]
  } else {
    filters.value.start_date = ''
    filters.value.end_date = ''
  }
  // 触发搜索
}

const handleReset = () => {
  dateRange.value = null
  // 重置其他 filters
}
</script>

<template>
  <el-date-picker
    v-model="dateRange"
    type="daterange"
    range-separator="to"
    start-placeholder="Start"
    end-placeholder="End"
    value-format="YYYY-MM-DD"
    @change="handleDateRangeChange"
  />
</template>
```

### 相关文件
- `/Users/liqingchao/workspace/assessment2/frontend/src/views/AdminRequirements.vue`
- `/Users/liqingchao/workspace/assessment2/frontend/src/views/AdminTasks.vue`

---

# Python Pylint 开发规范

## 导入顺序规范

Python 文件应按照以下顺序组织导入:

1. **标准库导入 (Standard Library)**
   - `import os`, `import re`, `import json`, `from datetime import datetime`
   - `from typing import List, Optional, Dict`

2. **第三方导入 (Third-Party)**
   - `from fastapi import APIRouter`
   - `from sqlalchemy.orm import Session`
   - `from pydantic import BaseModel`

3. **本地应用导入 (Local Application)**
   - `from model.user import UserModel`
   - `from schemas.portal import PortalServiceSchema`
   - `from service.portal_service import PortalService`

### 正确示例:
```python
# Standard library imports
import random
from datetime import datetime
from typing import List, Optional

# Third-party imports
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Local application imports
from model.user import UserModel
from schemas.portal import PortalSchema
from service.portal_service import PortalService
```

### 错误示例:
```python
from fastapi import APIRouter  # 第三方库
import random                  # 标准库 - 顺序错误
from model.user import UserModel  # 本地库
```

## 其他规范

### 1. 避免行尾空格 (Trailing Whitespace)
- 不要在行尾保留空格

### 2. 行长度限制
- 最大行长度: 120 字符

### 3. 异常处理
- 使用具体异常类型,避免使用裸 `except:`
```python
# 错误
try:
    pass
except:
    pass

# 正确
try:
    pass
except (ValueError, TypeError):
    pass
```

### 4. 避免重复导入
- 不要在函数内部重复导入已在上层导入的模块

### 5. 函数/方法注释
- 为所有公共方法和类添加 docstring

### 6. 比较操作符
- 使用 `is None` 而不是 `== None`

## Pylint 配置文件

项目根目录: `/Users/liqingchao/workspace/assessment2/backend/.pylintrc`

运行 pylint:
```bash
cd /Users/liqingchao/workspace/assessment2/backend/src
python -m pylint --rcfile=../.pylintrc <文件名>.py
```

### 记录日期
2026-03-13
