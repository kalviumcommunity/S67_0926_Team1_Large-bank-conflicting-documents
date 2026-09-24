import { Outlet } from "react-router-dom"

function AppLayout() {
  return (
    <div className="min-h-screen bg-slate-50">
      <Outlet />
    </div>
  )
}

export default AppLayout