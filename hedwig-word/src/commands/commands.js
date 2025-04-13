Office.onReady(() => {
  // Ready để nhận lệnh command từ ribbon
});

function action(event) {
  // Đây là lệnh mặc định gắn với nút mở taskpane
  console.log("Ribbon button clicked!");

  // Office yêu cầu bạn phải gọi event.completed() để không bị lỗi
  event.completed();
}

// Gắn hành vi này với tên action được khai trong manifest.xml
Office.actions.associate("action", action);
