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

  useEffect(() => {
    if (!showSlide) return
    const interval = setInterval(() => {
      setFade(true)
      setTimeout(() => {
        setCurrentIndex((prev) => (prev + 1) % images.length)
        setFade(false)
      }, 500)
    }, 5000)
    return () => clearInterval(interval)
  }, [currentIndex, showSlide])

  return (
    <div className="main-layout">
      <Header />

      <main className="main-content">
        {showSlide && (
          <div className="slideshow-shell">
            <div className="slideshow-container">
              <img
                src={images[currentIndex]}
                alt={`Slide ${currentIndex + 1}`}
                className={`slide-image ${fade ? 'fade-out' : 'fade-in'}`}
              />
              <div className="slide-overlay">
                <span className="slide-overlay__eyebrow">YoloHome · Smart living</span>
                <h2>Chào mừng đến với hệ thống nhà thông minh hiện đại</h2>

              </div>
            </div>
          </div>
        )}

        <div className="page-container">
          {showSlide && (
            <div className="features-content">
              <div className="feature">
                <Fingerprint size={40} className="feature-icon" />
                <div className="feature-text">CHẠM THÔNG MINH, <br /> SỐNG TRỌN VẸN</div>
              </div>
              <div className="feature">
                <ThermometerSun size={40} className="feature-icon" />
                <div className="feature-text">THẤU HIỂU MÔI TRƯỜNG, <br /> LÀM CHỦ KHÔNG GIAN</div>
              </div>
              <div className="feature">
                <Share2 size={40} className="feature-icon" />
                <div className="feature-text">KẾT NỐI TỐI GIẢN, <br /> TỐI ƯU TIỆN ÍCH</div>
              </div>
            </div>
          )}
          <Outlet />
        </div>
      </main>

      <Footer />
    </div>
  )
}

export default MainLayout
