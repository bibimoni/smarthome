export const uc4Scenarios = {
  list: {
    id: 'list',
    tabLabel: 'Màn hình 1 · Danh sách log',
    badge: 'Mô phỏng UC_4',
    headline: 'Activity history / Event log',
    subtext: 'Danh sách log gần nhất được sắp xếp theo thời gian giảm dần.',
    metrics: [
      { label: 'Bản ghi hiện có', value: '128' },
      { label: 'Thiết bị liên quan', value: '5' },
    ],
    filters: ['Hôm nay', 'Mọi thiết bị', 'Mọi sự kiện'],
    logs: [
      { time: '09:25', type: 'AUTO', device: 'Quạt', summary: 'Thiết bị trở về AUTO sau khi hết ghi đè.' },
      { time: '09:21', type: 'COMMAND', device: 'Quạt', summary: 'Người dùng bật quạt thủ công ở chế độ MANUAL.' },
      { time: '09:16', type: 'REFRESH', device: 'Dashboard', summary: 'Dữ liệu cảm biến được tải lại thành công.' },
    ],
  },
  filtered: {
    id: 'filtered',
    tabLabel: 'Màn hình 2 · Lọc lịch sử',
    badge: 'Áp dụng bộ lọc',
    headline: 'Danh sách sau khi lọc',
    subtext: 'Người dùng lọc theo thiết bị hoặc loại sự kiện để tìm đúng bản ghi cần xem.',
    metrics: [
      { label: 'Bộ lọc', value: 'Thiết bị: Quạt' },
      { label: 'Kết quả', value: '12' },
    ],
    filters: ['7 ngày gần nhất', 'Quạt', 'AUTO / COMMAND'],
    logs: [
      { time: '09:25', type: 'AUTO', device: 'Quạt', summary: 'Luật tự động được kích hoạt trở lại.' },
      { time: '09:20', type: 'MANUAL', device: 'Quạt', summary: 'Người dùng chuyển quạt sang MANUAL.' },
    ],
  },
  detail: {
    id: 'detail',
    tabLabel: 'Màn hình 3 · Chi tiết sự kiện',
    badge: 'Mở log chi tiết',
    headline: 'Chi tiết bản ghi sự kiện',
    subtext: 'Hệ thống hiển thị timestamp chính xác: dữ liệu cảm biến và trạng thái trước sau của thiết bị.',
    metrics: [
      { label: 'Mã sự kiện', value: '#LOG-0921' },
      { label: 'Thiết bị', value: 'Quạt' },
    ],
    detail: {
      title: 'Chi tiết log',
      rows: [
        { label: 'Timestamp', value: '2026-04-05 09:21:08' },
        { label: 'Loại sự kiện', value: 'COMMAND' },
        { label: 'Thiết bị', value: 'Quạt' },
        { label: 'Trạng thái trước', value: 'MANUAL / OFF' },
        { label: 'Trạng thái sau', value: 'MANUAL / ON' },
        { label: 'Dữ liệu cảm biến', value: 'Nhiệt độ 31°C · Độ ẩm 58%' },
      ],
    },
  },
  empty: {
    id: 'empty',
    tabLabel: 'Màn hình 4 · Chưa có log',
    badge: 'Danh sách rỗng',
    headline: 'Chưa có lịch sử hoạt động',
    subtext: 'Trạng thái rỗng được hiển thị khi hệ thống chưa phát sinh bản ghi nào.',
    metrics: [
      { label: 'Event log', value: '0' },
      { label: 'Trạng thái', value: 'Chờ dữ liệu' },
    ],
    emptyTitle: 'Chưa có lịch sử hoạt động',
    emptyBody: 'Khi hệ thống có cảnh báo: thao tác thủ công hoặc lỗi thiết bị: bản ghi sẽ xuất hiện tại đây.',
  },
  noResult: {
    id: 'noResult',
    tabLabel: 'Màn hình 5 · Bộ lọc không có kết quả',
    badge: 'Không tìm thấy',
    headline: 'Bộ lọc trả về 0 kết quả',
    subtext: 'Người dùng có thể giữ nguyên bộ lọc hiện tại hoặc thử lại với điều kiện khác.',
    metrics: [
      { label: 'Bộ lọc', value: 'Servo · ERROR' },
      { label: 'Kết quả', value: '0' },
    ],
    filters: ['Hôm nay', 'Servo', 'ERROR'],
    emptyTitle: 'Không tìm thấy sự kiện phù hợp',
    emptyBody: 'Không có bản ghi nào khớp với bộ lọc đang chọn.',
  },
  loadMore: {
    id: 'loadMore',
    tabLabel: 'Màn hình 6 · Tải thêm log',
    badge: 'Phân trang',
    headline: 'Tải thêm bản ghi cũ hơn',
    subtext: 'Hệ thống truy vấn thêm dữ liệu và nối vào danh sách hiện tại.',
    metrics: [
      { label: 'Đã tải', value: '40 log' },
      { label: 'Trang hiện tại', value: '2' },
    ],
    filters: ['30 ngày gần nhất', 'Mọi thiết bị', 'Mọi sự kiện'],
    logs: [
      { time: '09:25', type: 'AUTO', device: 'Quạt', summary: 'Thiết bị trở về AUTO sau khi hết ghi đè.' },
      { time: '09:21', type: 'COMMAND', device: 'Quạt', summary: 'Người dùng bật quạt thủ công ở chế độ MANUAL.' },
      { time: '08:47', type: 'ALERT', device: 'Nhiệt độ', summary: 'Nhiệt độ vượt ngưỡng cấu hình 30°C.' },
      { time: '08:35', type: 'SYSTEM', device: 'Controller', summary: 'Đồng bộ trạng thái thiết bị thành công.' },
    ],
  },
}

export const uc4Tabs = Object.values(uc4Scenarios).map(({ id, tabLabel }) => ({ id, label: tabLabel }))
