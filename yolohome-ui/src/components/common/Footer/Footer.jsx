import React from 'react'
import './Footer.scss'

const Footer = () => {
   return (
      <footer className="footer-container">
         <div className="footer-line"></div>

         <div className="footer-main-title">Giới thiệu về chúng tôi</div>

         <div className="footer-content">
            <div className="footer-column">
               <h3>Liên hệ</h3>
               <p>Địa chỉ: Toà nhà H6, Đại học Bách Khoa TP.HCM</p>
               <p>Email: antoany@8386hcmut.edu.vn</p>
               <p>Hotline: 012.3456.7890</p>
            </div>

            <div className="footer-column">
               <h3>Dịch vụ</h3>
               <ul>
                  <li>Giám sát thời gian thực</li>
                  <li>Thiết lập kịch bản tự động</li>
                  <li>Quản lý thiết bị thông minh</li>
               </ul>
            </div>

            <div className="footer-column">
               <h3>Hỗ trợ</h3>
               <ul>
                  <li>Chính sách bảo mật</li>
                  <li>Điều khoản sử dụng</li>
                  <li>Hướng dẫn cài đặt</li>
               </ul>
            </div>
         </div>

         <div className="footer-bottom">
            &copy; 2026 YoloHome Project - Hệ thống nhà thông minh tích hợp IoT
         </div>
      </footer>
   )
}

export default Footer
