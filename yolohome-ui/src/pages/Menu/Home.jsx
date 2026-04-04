import { useNavigate } from 'react-router-dom'
import './Home.scss'

function Home() {
  const navigate = useNavigate()

  return (
    <section className="home-shortcuts glass-panel">
      <div>
        <span className="home-shortcuts__eyebrow">Mockup FE đã triển khai</span>
        <h2>Chọn use case để xem giao diện</h2>
        <p>UC1 đã có đủ 4 màn hình và UC3 đã có đủ 5 màn hình bằng mock data.</p>
      </div>
      <div className="home-shortcuts__actions">
        <button type="button" className="ghost-pill is-dark" onClick={() => navigate('/dashboard')}>Mở UC1</button>
        <button type="button" className="ghost-pill" onClick={() => navigate('/device-control')}>Mở UC3</button>
      </div>
    </section>
  )
}

export default Home
