import type { ReactNode } from "react"
import type { Role, User } from "./types"

type IconName =
  | "grid" | "calendar" | "file" | "users" | "chart" | "settings" | "bell"
  | "search" | "plus" | "arrow" | "spark" | "clock" | "check" | "x"
  | "download" | "chevron" | "more" | "external" | "user" | "school" | "menu"

const paths: Record<IconName, ReactNode> = {
  grid: <><rect x="3" y="3" width="7" height="7" rx="2" /><rect x="14" y="3" width="7" height="7" rx="2" /><rect x="3" y="14" width="7" height="7" rx="2" /><rect x="14" y="14" width="7" height="7" rx="2" /></>,
  calendar: <><rect x="3" y="5" width="18" height="16" rx="3" /><path d="M16 3v4M8 3v4M3 10h18" /></>,
  file: <><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><path d="M14 2v6h6M8 13h8M8 17h5" /></>,
  users: <><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" /></>,
  chart: <><path d="M3 3v18h18" /><path d="m7 16 4-5 4 3 5-7" /></>,
  settings: <><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-2.83 2.83-.06-.06A1.7 1.7 0 0 0 15 19.4a1.7 1.7 0 0 0-1 .6 1.7 1.7 0 0 0-.4 1.1V21H9.6v-.09A1.7 1.7 0 0 0 8.5 19.4a1.7 1.7 0 0 0-1.88.34l-.06.06-2.83-2.83.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-.6-1 1.7 1.7 0 0 0-1.1-.4H3V9.6h.09A1.7 1.7 0 0 0 4.6 8.5a1.7 1.7 0 0 0-.34-1.88l-.06-.06 2.83-2.83.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-.6 1.7 1.7 0 0 0 .4-1.1V3h4v.09A1.7 1.7 0 0 0 15.5 4.6a1.7 1.7 0 0 0 1.88-.34l.06-.06 2.83 2.83-.06.06A1.7 1.7 0 0 0 19.4 9c.14.37.36.7.64.98.3.28.68.43 1.08.42H21v4h-.09A1.7 1.7 0 0 0 19.4 15Z" /></>,
  bell: <><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M13.7 21a2 2 0 0 1-3.4 0" /></>,
  search: <><circle cx="11" cy="11" r="7" /><path d="m20 20-4-4" /></>,
  plus: <path d="M12 5v14M5 12h14" />,
  arrow: <><path d="M5 12h14M13 6l6 6-6 6" /></>,
  spark: <path d="m12 3-1.3 4.1a5 5 0 0 1-3.2 3.2L3 12l4.5 1.7a5 5 0 0 1 3.2 3.2L12 21l1.3-4.1a5 5 0 0 1 3.2-3.2L21 12l-4.5-1.7a5 5 0 0 1-3.2-3.2L12 3Z" />,
  clock: <><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></>,
  check: <path d="m5 12 4 4L19 6" />,
  x: <path d="M6 6l12 12M18 6 6 18" />,
  download: <><path d="M12 3v12M7 10l5 5 5-5M5 21h14" /></>,
  chevron: <path d="m9 18 6-6-6-6" />,
  more: <><circle cx="5" cy="12" r="1" /><circle cx="12" cy="12" r="1" /><circle cx="19" cy="12" r="1" /></>,
  external: <><path d="M15 3h6v6M10 14 21 3" /><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" /></>,
  user: <><circle cx="12" cy="8" r="4" /><path d="M4 21a8 8 0 0 1 16 0" /></>,
  school: <><path d="m3 10 9-6 9 6-9 6-9-6Z" /><path d="M7 13v5c3 2 7 2 10 0v-5M21 10v7" /></>,
  menu: <path d="M4 7h16M4 12h16M4 17h16" />,
}

export function Icon({ name, size = 18, className = "" }: {
  name: IconName
  size?: number
  className?: string
}) {
  return (
    <svg className={className} width={size} height={size} viewBox="0 0 24 24"
      fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"
      strokeLinejoin="round" aria-hidden="true">
      {paths[name]}
    </svg>
  )
}

export function Status({ value }: { value: string }) {
  const tone: Record<string, string> = {
    Pending: "status-pending",
    Awaiting: "status-progress",
    "In Progress": "status-progress",
    Approved: "status-approved",
    Rejected: "status-rejected",
    Attended: "status-attended",
  }
  return <span className={`status ${tone[value] || ""}`}><i />{value}</span>
}

export function Metric({ label, value, note, icon, tone }: {
  label: string
  value: number
  note: string
  icon: IconName
  tone: string
}) {
  return (
    <article className={`metric ${tone}`}>
      <div className="metric-top"><span className="metric-icon"><Icon name={icon} /></span></div>
      <div className="metric-value">{value.toString().padStart(2, "0")}</div>
      <strong>{label}</strong>
      <small>{note}</small>
    </article>
  )
}

export interface FilterItem {
  label: string
  value: string
}

export function FilterPills({ items, active, onChange }: {
  items: FilterItem[]
  active: string
  onChange: (value: string) => void
}) {
  return (
    <div className="filter-pills">
      {items.map((item) => (
        <button type="button" key={item.value} onClick={() => onChange(item.value)}
          className={active === item.value ? "active" : ""}>
          {item.label}
        </button>
      ))}
    </div>
  )
}

export function Modal({ title, close, children }: {
  title: string
  close: () => void
  children: ReactNode
}) {
  return (
    <div className="modal-wrap" role="dialog" aria-modal="true" aria-label={title}>
      <button type="button" className="modal-backdrop" onClick={close} aria-label="Close" />
      <div className="modal">
        <div className="modal-head">
          <div><span className="eyebrow">ATTENEASE WORKFLOW</span><h2>{title}</h2></div>
          <button type="button" className="icon-btn" onClick={close} aria-label="Close dialog"><Icon name="x" /></button>
        </div>
        {children}
      </div>
    </div>
  )
}

function roleNav(role: Role) {
  if (role === "student") return [["grid", "Dashboard"], ["file", "My requests"], ["calendar", "Explore events"]]
  if (role === "coordinator") return [["grid", "Overview"], ["file", "Requests"], ["calendar", "My events"], ["chart", "Insights"]]
  return [["grid", "Overview"], ["file", "Approvals"], ["users", "Student activity"], ["chart", "Reports"]]
}

export function Sidebar({ user, open, close }: {
  user: User
  open: boolean
  close: () => void
}) {
  const nav = roleNav(user.role)
  const pulse = user.role === "student"
    ? { label: "My requests", value: "LIVE", note: "Personal attendance" }
    : user.role === "coordinator"
      ? { label: "Review queue", value: "LIVE", note: "Your event requests" }
      : { label: "Class activity", value: "LIVE", note: user.division || "Your division" }
  const initials = user.full_name.split(/\s+/).map((part) => part[0]).join("").slice(0, 2).toUpperCase()
  return (
    <>
      {open && <button className="sidebar-scrim" onClick={close} aria-label="Close menu" />}
      <aside className={`sidebar ${open ? "sidebar-open" : ""}`}>
        <div className="sidebar-glow" /><div className="sidebar-grid" />
        <div className="brand">
          <span className="brand-mark"><Icon name="check" size={18} /></span>
          <span><strong>Atten<span>Ease</span></strong><small>Campus command center</small></span>
          <i className="brand-signal" />
        </div>
        <div className="nav-label"><span>Workspace</span><i /></div>
        <nav>
          {nav.map(([icon, label], index) => (
            <button type="button" className={`nav-item ${index === 0 ? "active" : ""}`} key={label} onClick={close}>
              <span className="nav-icon"><Icon name={icon as IconName} /></span>
              <span className="nav-copy">{label}<small>0{index + 1}</small></span>
              {index === 0 && <span className="nav-arrow"><Icon name="chevron" size={13} /></span>}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="pulse-card">
            <div className="pulse-card-head"><span><Icon name="spark" size={14} /></span><small>{pulse.label}</small><i /></div>
            <div className="pulse-card-value"><strong>{pulse.value}</strong><div><span>ACCOUNT</span><small>{pulse.note}</small></div></div>
            <div className="pulse-line">{[28, 48, 38, 68, 54, 84, 72, 96].map((height, index) => <i key={index} style={{ height: `${height}%` }} />)}</div>
          </div>
          <a className="nav-item settings-item" href="/auth/logout/">
            <span className="nav-icon"><Icon name="settings" /></span><span className="nav-copy">Sign out</span><Icon name="chevron" size={13} />
          </a>
          <div className="profile">
            <span className="avatar">{initials}</span>
            <span><strong>{user.full_name}</strong><small>{user.role_label}{user.division ? ` · ${user.division}` : ""}</small></span>
          </div>
        </div>
      </aside>
    </>
  )
}

export function Topbar({ onMenu }: { onMenu: () => void }) {
  return (
    <header className="topbar">
      <button type="button" className="mobile-menu" onClick={onMenu} aria-label="Open menu"><Icon name="menu" /></button>
      <div className="search"><Icon name="search" /><input placeholder="Search anything..." aria-label="Search" /><kbd>⌘ K</kbd></div>
      <div className="top-actions"><span className="live"><i /> Live system</span><button type="button" className="icon-btn" aria-label="Notifications"><Icon name="bell" /></button></div>
    </header>
  )
}

export function Feedback({ error, success, loading, onRetry }: {
  error: string
  success: string
  loading: boolean
  onRetry: () => void
}) {
  return (
    <>
      {loading && <div className="state-banner" role="status">Loading your dashboard…</div>}
      {error && <div className="state-banner state-error" role="alert">{error}<button type="button" onClick={onRetry}>Retry</button></div>}
      {success && <div className="state-banner state-success" role="status">{success}</div>}
    </>
  )
}

export function EmptyState({ children }: { children: ReactNode }) {
  return <div className="empty-state"><span className="empty-icon"><Icon name="file" size={23} /></span><strong>Nothing to show yet</strong><p>{children}</p></div>
}
