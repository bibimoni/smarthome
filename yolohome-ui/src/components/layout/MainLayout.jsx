import { useState, useEffect } from 'react'
import Header from '@components/common/Header/Header.jsx'
import Footer from '@components/common/Footer/Footer.jsx'
import { Outlet, useLocation } from 'react-router-dom'
import './MainLayout.scss'

import sm1 from '@assets/common/sm1.jpg'
import sm2 from '@assets/common/sm2.jpg'
import sm3 from '@assets/common/sm3.jpg'
import sm4 from '@assets/common/sm4.jpg'
import sm5 from '@assets/common/sm5.jpg'

import { Fingerprint, ThermometerSun, Share2 } from 'lucide-react'

function MainLayout() {
   const location = useLocation()
   const showSlide = location.pathname === '/'

   const images = [sm1, sm2, sm3, sm4, sm5]
   const [currentIndex, setCurrentIndex] = useState(0)
   const [fade, setFade] = useState(false)

   // Tự động chuyển slide mỗi 5s
   useEffect(() => {
      if (!showSlide) return
      const interval = setInterval(() => {
         handleNext()
      }, 5000)
      return () => clearInterval(interval)
   }, [currentIndex, showSlide])

   const handleNext = () => {
      setFade(true)
      setTimeout(() => {
         setCurrentIndex((prev) => (prev + 1) % images.length)
         setFade(false)
      }, 500)
   }

   return (
      <div className="main-layout">
         <Header />

         <main className="main-content">
            {/* Slideshow chỉ hiện ở Trang chủ */}
            {showSlide && (
               <div className="slideshow-container">
                  <img
                     src={images[currentIndex]}
                     alt={`Slide ${currentIndex + 1}`}
                     className={`slide-image ${fade ? 'fade-out' : 'fade-in'}`}
                  />
                  <div className="slide-overlay">
                     <h2>Chào mừng đến với YoloHome</h2>
                     <p>Hệ thống quản lý nhà thông minh hiện đại</p>
                  </div>
               </div>
            )}

            {/* Nội dung của các trang con (Login, Dashboard, v.v.) */}
            <div className="page-container">
               <div className="features-content">
                  <div className="feature">
                     <Fingerprint size={40} className="feature-icon" />
                     <div className="feature-text">
                        CHẠM THÔNG MINH,
                        <br /> SỐNG TRỌN VẸN
                     </div>
                  </div>
                  <div className="feature">
                     <ThermometerSun size={40} className="feature-icon" />
                     <div className="feature-text">
                        THẤU HIỂU MÔI TRƯỜNG,
                        <br /> LÀM CHỦ KHÔNG GIAN
                     </div>
                  </div>
                  <div className="feature">
                     <Share2 size={40} className="feature-icon" />
                     <div className="feature-text">
                        KẾT NỐI TỐI GIẢN,
                        <br /> TỐI ƯU TIỆN ÍCH
                     </div>
                  </div>
               </div>
               <Outlet />
            </div>
         </main>

         <Footer />
      </div>
   )
}

export default MainLayout
