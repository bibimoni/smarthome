export const uc2Scenarios = {
  list: {
    id: 'list',
    tabLabel: 'Màn hình 1 · Danh sách ngưỡng',
    badge: 'Mô phỏng UC_2',
    headline: 'Quản lý ngưỡng môi trường',
    subtext: 'Danh sách quy tắc đang hoạt động được đồng bộ tới bộ điều khiển trung tâm.',
    summary: [
      { label: 'Quy tắc hiện có', value: '3' },
      { label: 'Đang active', value: '2' },
    ],
    rules: [
      { id: 1, sensor: 'Nhiệt độ', condition: '> 30°C', output: 'Quạt', action: 'Bật', status: 'ACTIVE' },
      { id: 2, sensor: 'Ánh sáng', condition: '< 120 lux', output: 'Đèn LED', action: 'Bật', status: 'ACTIVE' },
      { id: 3, sensor: 'Độ ẩm', condition: '< 40%', output: 'LCD', action: 'Hiển thị cảnh báo', status: 'INACTIVE' },
    ],
    side: {
      title: 'Tóm tắt quy tắc',
      text: 'Hệ thống kiểm tra điều kiện cảm biến định kỳ và áp dụng những quy tắc đang Active.',
      chips: ['Thêm ngưỡng mới', 'Chỉnh sửa', 'Bật/Tắt', 'Xóa'],
    },
  },
  empty: {
    id: 'empty',
    tabLabel: 'Màn hình 2 · Chưa có ngưỡng',
    badge: 'Danh sách rỗng',
    headline: 'Chưa có ngưỡng nào được cấu hình',
    subtext: 'Giao diện rỗng hiển thị nút kêu gọi tạo quy tắc đầu tiên.',
    summary: [
      { label: 'Quy tắc hiện có', value: '0' },
      { label: 'Trạng thái', value: 'Sẵn sàng tạo mới' },
    ],
    emptyTitle: 'Chưa có ngưỡng nào được cấu hình',
    emptyBody: 'Tạo quy tắc mới để tự động bật thiết bị khi cảm biến vượt ngưỡng mong muốn.',
  },
  create: {
    id: 'create',
    tabLabel: 'Màn hình 3 · Thêm ngưỡng',
    badge: 'Tạo quy tắc mới',
    headline: 'Form cấu hình ngưỡng',
    subtext: 'Người dùng chọn cảm biến: giá trị ngưỡng: thiết bị đầu ra và hành động kích hoạt.',
    summary: [
      { label: 'Cảm biến', value: 'Nhiệt độ' },
      { label: 'Thiết bị', value: 'Quạt' },
    ],
    formTitle: 'Thêm ngưỡng mới',
    fields: [
      { label: 'Cảm biến', value: 'Nhiệt độ' },
      { label: 'Điều kiện', value: 'Lớn hơn' },
      { label: 'Giá trị ngưỡng', value: '30°C' },
      { label: 'Thiết bị đầu ra', value: 'Quạt' },
      { label: 'Hành động', value: 'Bật ON' },
    ],
  },
  edit: {
    id: 'edit',
    tabLabel: 'Màn hình 4 · Chỉnh sửa ngưỡng',
    badge: 'Cập nhật quy tắc',
    headline: 'Chỉnh sửa ngưỡng đã tồn tại',
    subtext: 'Form được nạp sẵn dữ liệu hiện tại để người dùng cập nhật nhanh.',
    summary: [
      { label: 'Quy tắc đang sửa', value: '#02' },
      { label: 'Lần sửa cuối', value: '09:28' },
    ],
    formTitle: 'Chỉnh sửa ngưỡng',
    fields: [
      { label: 'Cảm biến', value: 'Ánh sáng' },
      { label: 'Điều kiện', value: 'Nhỏ hơn' },
      { label: 'Giá trị ngưỡng', value: '100 lux' },
      { label: 'Thiết bị đầu ra', value: 'Đèn LED' },
      { label: 'Hành động', value: 'Bật ON' },
    ],
  },
  invalid: {
    id: 'invalid',
    tabLabel: 'Màn hình 5 · Dữ liệu không hợp lệ',
    badge: 'Xử lý lỗi nhập liệu',
    headline: 'Không thể lưu quy tắc',
    subtext: 'Hệ thống giữ nguyên form và báo rõ các trường đang sai hoặc còn thiếu.',
    summary: [
      { label: 'Lỗi', value: '2 trường' },
      { label: 'Trạng thái', value: 'Chưa lưu' },
    ],
    formTitle: 'Thêm ngưỡng mới',
    fields: [
      { label: 'Cảm biến', value: '—', error: 'Bắt buộc chọn cảm biến' },
      { label: 'Giá trị ngưỡng', value: 'abc', error: 'Giá trị phải là số hợp lệ' },
      { label: 'Thiết bị đầu ra', value: 'Quạt' },
      { label: 'Hành động', value: 'Bật ON' },
    ],
    alert: 'Dữ liệu đầu vào không hợp lệ hoặc quy tắc xung đột với ngưỡng đã tồn tại.',
  },
}

export const uc2Tabs = Object.values(uc2Scenarios).map(({ id, tabLabel }) => ({ id, label: tabLabel }))
