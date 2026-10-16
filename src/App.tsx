import { useCallback, useEffect, useState } from "react"
import { ApiError, api } from "./api"
import { Feedback, Icon, Sidebar, Topbar } from "./components"
import {
  CoordinatorDashboard,
  StudentDashboard,
  TeacherDashboard,
} from "./dashboards"
import type { DashboardData, Role, User } from "./types"

const emptyDashboard: DashboardData = {
  stats: {},
  requests: [],
  events: [],
  student_activity: [],
}

export default function App() {
  const [user, setUser] = useState<User | null>(null)
  const [data, setData] = useState<DashboardData>(emptyDashboard)
  const [filter, setFilter] = useState("")
  const [month, setMonth] = useState("")
  const [loading, setLoading] = useState(true)
  const [authLoading, setAuthLoading] = useState(true)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const [menu, setMenu] = useState(false)

  const loadDashboard = useCallback(async (
    role: Role,
    status = filter,
    selectedMonth = month,
  ) => {
    setLoading(true)
    setError("")
    try {
      const result = await api.dashboard(role, status, selectedMonth)
      setData(result)
    } catch (cause) {
      if (cause instanceof ApiError && cause.status === 401) {
        window.location.assign("/auth/login/")
        return
      }
      setError(cause instanceof Error ? cause.message : "Could not load dashboard data.")
    } finally {
      setLoading(false)
    }
  }, [filter, month])

  useEffect(() => {
    let cancelled = false
    api.session().then(({ user: sessionUser }) => {
      if (cancelled) return
      if (!["student", "coordinator", "teacher"].includes(sessionUser.role)) {
        setError("This dashboard is available to students, event coordinators, and class teachers.")
        setAuthLoading(false)
        setLoading(false)
        return
      }
      setUser(sessionUser)
      setAuthLoading(false)
    }).catch((cause: unknown) => {
      if (cancelled) return
      if (cause instanceof ApiError && cause.status === 401) {
        window.location.assign("/auth/login/")
        return
      }
      setError(cause instanceof Error ? cause.message : "Could not verify your signed-in account.")
      setAuthLoading(false)
      setLoading(false)
    })
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    if (user) void loadDashboard(user.role)
  }, [user, filter, month, loadDashboard])

  useEffect(() => {
    if (!success) return
    const timer = window.setTimeout(() => setSuccess(""), 4000)
    return () => window.clearTimeout(timer)
  }, [success])

  const refresh = useCallback(async () => {
    if (user) await loadDashboard(user.role)
  }, [loadDashboard, user])

  const announceSuccess = useCallback(async (message: string) => {
    setSuccess(message)
    setError("")
    await refresh()
  }, [refresh])

  if (authLoading) {
    return <div className="app app-state"><div className="state-card"><span className="loading-mark"><Icon name="check" /></span><strong>Checking your account…</strong><small>Loading your role-specific workspace</small></div></div>
  }

  if (!user) {
    return <div className="app app-state"><div className="state-card"><span className="loading-mark error-mark"><Icon name="x" /></span><strong>Dashboard unavailable</strong><p role="alert">{error || "Could not load your account."}</p><a className="secondary-btn" href="/auth/login/">Return to sign in</a></div></div>
  }

  return (
    <div className={`app role-${user.role}`}>
      <Sidebar user={user} open={menu} close={() => setMenu(false)} />
      <main className="main">
        <Topbar onMenu={() => setMenu(true)} />
        <Feedback error={error} success={success} loading={loading} onRetry={() => void refresh()} />
        {user.role === "student" ? (
          <StudentDashboard
            user={user}
            data={data}
            filter={filter}
            onFilter={setFilter}
            onRefresh={refresh}
            onSuccess={announceSuccess}
          />
        ) : user.role === "coordinator" ? (
          <CoordinatorDashboard
            user={user}
            data={data}
            filter={filter}
            onFilter={setFilter}
            onRefresh={refresh}
            onSuccess={announceSuccess}
          />
        ) : (
          <TeacherDashboard
            user={user}
            data={data}
            filter={filter}
            onFilter={setFilter}
            onRefresh={refresh}
            onSuccess={announceSuccess}
            month={month}
            onMonth={setMonth}
          />
        )}
      </main>
    </div>
  )
}
