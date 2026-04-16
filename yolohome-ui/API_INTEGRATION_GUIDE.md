# FE API Integration Guide

Tài liệu này dùng để thống nhất cách frontend `yolohome-ui` gọi API tới backend Flask của dự án `smarthome`.

## 1. Mục tiêu

Frontend không gọi API trực tiếp rải rác trong nhiều component. Mọi request nên đi qua lớp `services` để:

- dễ bảo trì
- dễ debug
- tái sử dụng được
- thống nhất cách gắn token và xử lý lỗi

## 2. Base URL

Frontend dùng `VITE_API_BASE_URL` trong `.env`:

```env
VITE_API_BASE_URL=http://localhost:5000
```

Nếu backend chạy ở môi trường dev khác, chỉ đổi biến này rồi restart Vite.

File dùng chung:

- `src/services/apiClient.js`

Ví dụ:

```js
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

export async function apiFetch(path, options = {}) {
  const token = localStorage.getItem("access_token");

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error || data.message || "API request failed");
  }

  return data;
}
```

## 3. Cấu trúc folder nên dùng

```text
src/
  services/
    apiClient.js
    authApi.js
    sensorApi.js
    actuatorApi.js
    thresholdApi.js
    sceneApi.js
    logApi.js
```

Quy ước:

- `apiClient.js`: nơi duy nhất xử lý base URL, headers, token, error chung
- `xxxApi.js`: gom hàm gọi API theo từng domain
- page/component chỉ gọi hàm từ `services`

## 4. Luồng gọi API chuẩn

Mọi trang nên follow cùng một pattern:

1. component mount
2. set `loading = true`
3. gọi hàm trong `services`
4. set data khi thành công
5. set error khi thất bại
6. set `loading = false`

Mẫu:

```js
const [loading, setLoading] = useState(true);
const [error, setError] = useState("");
const [data, setData] = useState(null);

useEffect(() => {
  async function loadData() {
    try {
      setLoading(true);
      setError("");
      const res = await someApi();
      setData(res);
    } catch (err) {
      setError(err.message || "Có lỗi xảy ra");
    } finally {
      setLoading(false);
    }
  }

  loadData();
}, []);
```

## 5. Auth

File:

- `src/services/authApi.js`

Nên có các hàm:

```js
import { apiFetch } from "./apiClient";

export function login(payload) {
  return apiFetch("/api/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function register(payload) {
  return apiFetch("/api/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function forgotPassword(payload) {
  return apiFetch("/api/auth/forgot-password", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function resetPassword(payload) {
  return apiFetch("/api/auth/reset-password", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getProfile() {
  return apiFetch("/api/auth/me");
}
```

Map trang:

- `Login.jsx` -> `login`
- `Register.jsx` -> `register`
- `ForgetPassword.jsx` -> `forgotPassword`, `resetPassword`

Luồng login:

1. user submit form
2. gọi `login({ email, password })`
3. nhận `access_token`
4. lưu vào `localStorage` với key duy nhất là `access_token`
5. update auth context
6. navigate sang trang chính

## 6. Dashboard / UC1

File:

- `src/services/sensorApi.js`
- `src/services/logApi.js`

Ví dụ:

```js
import { apiFetch } from "./apiClient";

export function getSensors() {
  return apiFetch("/api/sensors/");
}

export function getSensorData(sensorId, hours = 24) {
  return apiFetch(`/api/sensors/${sensorId}/data?hours=${hours}`);
}

export function getSensorStatistics(sensorId, hours = 24) {
  return apiFetch(`/api/sensors/${sensorId}/statistics?hours=${hours}`);
}
```

```js
import { apiFetch } from "./apiClient";

export function getLogsSummary(days = 1) {
  return apiFetch(`/api/logs/summary?days=${days}`);
}

export function getRecentLogs(page = 1, perPage = 5) {
  return apiFetch(`/api/logs/?page=${page}&per_page=${perPage}`);
}
```

Map backend:

- `GET /api/sensors/`
- `GET /api/sensors/{id}/data`
- `GET /api/sensors/{id}/statistics`
- `GET /api/logs/summary`
- `GET /api/logs/`

Luồng dashboard:

1. lấy danh sách sensor
2. lấy history cho sensor cần vẽ chart
3. lấy summary log cho khu vực cảnh báo
4. nút refresh gọi lại các request trên

## 7. Thresholds / UC2

File:

- `src/services/thresholdApi.js`

Ví dụ:

```js
import { apiFetch } from "./apiClient";

export function getThresholdRules() {
  return apiFetch("/api/thresholds/");
}

export function createThresholdRule(payload) {
  return apiFetch("/api/thresholds/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateThresholdRule(id, payload) {
  return apiFetch(`/api/thresholds/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteThresholdRule(id) {
  return apiFetch(`/api/thresholds/${id}`, {
    method: "DELETE",
  });
}

export function toggleThresholdRule(id) {
  return apiFetch(`/api/thresholds/${id}/toggle`, {
    method: "POST",
  });
}
```

Map backend:

- `GET /api/thresholds/`
- `POST /api/thresholds/`
- `PUT /api/thresholds/{id}`
- `DELETE /api/thresholds/{id}`
- `POST /api/thresholds/{id}/toggle`

Luồng trang:

1. load danh sách rule
2. mở modal tạo rule -> gọi create
3. sửa -> gọi update
4. bật/tắt -> gọi toggle
5. xóa -> gọi delete
6. reload list sau thao tác

## 8. Device Control / UC3

File:

- `src/services/actuatorApi.js`

Ví dụ:

```js
import { apiFetch } from "./apiClient";

export function getActuators() {
  return apiFetch("/api/actuators/");
}

export function getAllActuatorStatus() {
  return apiFetch("/api/actuators/status");
}

export function controlActuator(id, payload) {
  return apiFetch(`/api/actuators/${id}/control`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function toggleActuator(id) {
  return apiFetch(`/api/actuators/${id}/toggle`, {
    method: "POST",
  });
}

export function setActuatorMode(id, mode) {
  return apiFetch(`/api/actuators/${id}/mode`, {
    method: "POST",
    body: JSON.stringify({ mode }),
  });
}

export function setActuatorValue(id, value) {
  return apiFetch(`/api/actuators/${id}/value`, {
    method: "POST",
    body: JSON.stringify({ value }),
  });
}
```

Map backend:

- `GET /api/actuators/`
- `GET /api/actuators/status`
- `POST /api/actuators/{id}/control`
- `POST /api/actuators/{id}/toggle`
- `POST /api/actuators/{id}/mode`
- `POST /api/actuators/{id}/value`

## 9. Activity History / UC4

File:

- `src/services/logApi.js`

Ví dụ:

```js
import { apiFetch } from "./apiClient";

export function getLogs(params = "") {
  return apiFetch(`/api/logs/${params ? `?${params}` : ""}`);
}

export function getLogTypes() {
  return apiFetch("/api/logs/types");
}

export function getLogsSummary(days = 7) {
  return apiFetch(`/api/logs/summary?days=${days}`);
}

export function getChartData(days = 7, groupBy = "day") {
  return apiFetch(`/api/logs/chart-data?days=${days}&group_by=${groupBy}`);
}
```

Map backend:

- `GET /api/logs/`
- `GET /api/logs/types`
- `GET /api/logs/summary`
- `GET /api/logs/chart-data`

## 10. Scenes / UC5

File:

- `src/services/sceneApi.js`

Ví dụ:

```js
import { apiFetch } from "./apiClient";

export function getScenes() {
  return apiFetch("/api/scenes/");
}

export function getScene(id) {
  return apiFetch(`/api/scenes/${id}`);
}

export function createScene(payload) {
  return apiFetch("/api/scenes/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateScene(id, payload) {
  return apiFetch(`/api/scenes/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteScene(id) {
  return apiFetch(`/api/scenes/${id}`, {
    method: "DELETE",
  });
}

export function executeScene(id) {
  return apiFetch(`/api/scenes/${id}/execute`, {
    method: "POST",
  });
}
```

Map backend:

- `GET /api/scenes/`
- `GET /api/scenes/{id}`
- `POST /api/scenes/`
- `PUT /api/scenes/{id}`
- `DELETE /api/scenes/{id}`
- `POST /api/scenes/{id}/execute`

## 11. Quy ước xử lý trạng thái

Mỗi page nên có tối thiểu:

- `loading`
- `error`
- `empty state`

Ví dụ:

```js
if (loading) return <div>Đang tải...</div>;
if (error) return <div>{error}</div>;
if (!data?.length) return <div>Chưa có dữ liệu</div>;
```

## 12. Quy ước token

Toàn dự án frontend chỉ dùng một key:

```js
localStorage.getItem("access_token")
```

Không dùng song song cả `token` và `access_token`.

## 13. Debug checklist

Khi API lỗi, kiểm tra theo thứ tự:

1. backend có đang chạy không
2. `VITE_API_BASE_URL` đúng chưa
3. đã restart Vite sau khi đổi `.env` chưa
4. request URL đúng chưa
5. request payload đúng chưa
6. tab `Network` trả status gì
7. backend log có traceback không

## 14. Ghi chú quan trọng

Docs và code backend hiện tại có vài điểm chưa khớp hoàn toàn. Khi làm frontend:

- ưu tiên bám code backend thật
- nếu docs khác code, dùng code đang chạy
- test bằng `Network` và response thực tế thay vì đoán theo UI

## 15. Kết luận

Nguyên tắc chung cho team:

- mọi request đi qua `apiClient.js`
- mọi nhóm API đi qua `services`
- page chỉ lo hiển thị và quản lý state UI
- thống nhất `access_token`
- luôn có `loading`, `error`, `empty state`

