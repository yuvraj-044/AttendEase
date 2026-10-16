import { useState, type FormEvent, type ReactNode } from "react"
import { api } from "./api"
import { EmptyState, FilterPills, Icon, Metric, Modal, Status } from "./components"
import type { AttendanceRequest, DashboardData, EventItem, StudentActivity, User } from "./types"

type CommonProps = {
  user: User
  data: DashboardData
  filter: string
  onFilter: (value: string) => void
  onRefresh: () => void
  onSuccess: (message: string) => void
}

function initials(name: string) {
  return name.split(/\s+/).map((part) => part[0]).join("").slice(0, 2).toUpperCase()
}

function dateLabel(value: string) {
  if (!value) return "—"
  return new Intl.DateTimeFormat("en-GB", { day: "2-digit", month: "short", year: "numeric" }).format(new Date(`${value}T00:00:00`))
}

function submittedLabel(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return "—"
  return new Intl.DateTimeFormat("en", { day: "2-digit", month: "short", hour: "numeric", minute: "2-digit" }).format(date)
}

function statusText(item: AttendanceRequest, role: User["role"]) {
  if (item.status === "pending") return "Pending"
  if (item.status === "coordinator_approved") {
    if (role === "coordinator") return "Approved"
    if (role === "teacher") return "Awaiting"
    return "In Progress"
  }
  if (item.status === "teacher_approved") return "Approved"
  return "Rejected"
}

function EmptyPanel({ message }: { message: string }) {
  return <div className="table-empty"><EmptyState>{message}</EmptyState></div>
}

function DataTable({ children, headers }: { children: ReactNode; headers: string[] }) {
  return (
    <div className="table-scroll"><table><thead><tr>{headers.map((header, index) => <th key={`${header}-${index}`}>{header}</th>)}</tr></thead><tbody>{children}</tbody></table></div>
  )
}

function RequestForm({ events, close, onSubmit }: {
  events: EventItem[]
  close: () => void
  onSubmit: (payload: Record<string, string | number>) => Promise<void>
}) {
  const [type, setType] = useState<"coordinator" | "open">("coordinator")
  const [eventId, setEventId] = useState("")
  const [reason, setReason] = useState("")
  const [externalName, setExternalName] = useState("")
  const [college, setCollege] = useState("")
  const [location, setLocation] = useState("")
  const [date, setDate] = useState("")
  const [time, setTime] = useState("")
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState("")

  async function submit(event: FormEvent) {
    event.preventDefault()
    setSaving(true)
    setError("")
    const payload: Record<string, string | number> = { event_type: type, reason }
    if (type === "coordinator") payload.event = Number(eventId)
    else Object.assign(payload, {
      external_event_name: externalName,
      external_college_name: college,
      external_event_location: location,
      external_event_date: date,
      external_event_time: time,
    })
    try {
      await onSubmit(payload)
      close()
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not submit the request.")
    } finally {
      setSaving(false)
    }
  }

  return (
    <form className="form-body" onSubmit={submit}>
      <div>
        <label>Event type</label>
        <div className="choice-row">
          <button type="button" className={type === "coordinator" ? "active" : ""} onClick={() => setType("coordinator")}><Icon name="school" />Internal event</button>
          <button type="button" className={type === "open" ? "active" : ""} onClick={() => setType("open")}><Icon name="external" />Open / external</button>
        </div>
      </div>
      {type === "coordinator" ? (
        <div><label htmlFor="request-event">Event</label><select id="request-event" className="form-select" required value={eventId} onChange={(event) => setEventId(event.target.value)}><option value="">Choose an active event</option>{events.map((item) => <option key={item.id} value={item.id}>{item.name} · {dateLabel(item.date)}</option>)}</select></div>
      ) : (
        <>
          <div className="field-grid">
            <div><label htmlFor="external-name">Event name</label><input id="external-name" required value={externalName} onChange={(event) => setExternalName(event.target.value)} placeholder="Event name" /></div>
            <div><label htmlFor="external-date">Event date</label><input id="external-date" required type="date" value={date} onChange={(event) => setDate(event.target.value)} /></div>
          </div>
          <div className="field-grid">
            <div><label htmlFor="external-college">Host college</label><input id="external-college" required value={college} onChange={(event) => setCollege(event.target.value)} placeholder="College or institution" /></div>
            <div><label htmlFor="external-location">Venue / location</label><input id="external-location" required value={location} onChange={(event) => setLocation(event.target.value)} placeholder="Venue or city" /></div>
          </div>
          <div><label htmlFor="external-time">Event time</label><input id="external-time" required type="time" value={time} onChange={(event) => setTime(event.target.value)} /></div>
        </>
      )}
      <div><label htmlFor="request-reason">Reason for attendance request</label><textarea id="request-reason" required rows={4} value={reason} onChange={(event) => setReason(event.target.value)} placeholder="Tell your reviewer why you want to attend…" /></div>
      <div className="workflow-hint"><span><Icon name="user" /></span><div><strong>{type === "coordinator" ? "Two-stage approval" : "Direct teacher approval"}</strong><small>{type === "coordinator" ? "Coordinator review → Class teacher review" : "This request goes straight to your class teacher"}</small></div></div>
      {error && <p className="form-error" role="alert">{error}</p>}
      <div className="modal-actions"><button type="button" className="secondary-btn" onClick={close}>Cancel</button><button className="primary-btn" disabled={saving}>{saving ? "Sending…" : "Send request"} <Icon name="arrow" /></button></div>
    </form>
  )
}

function RequestDetail({ item, role }: { item: AttendanceRequest; role: User["role"] }) {
  const coordinatorReviewed = item.status !== "pending"
  const teacherReviewed = item.status === "teacher_approved" || item.status === "teacher_rejected"
  const rejected = item.status.endsWith("rejected")
  return (
    <div className="detail-body">
      <div className="detail-status"><Status value={statusText(item, role)} /><span>Submitted {submittedLabel(item.created_at)}</span></div>
      <div className="detail-grid">
        <div><small>Event type</small><strong>{item.event_type_label}</strong></div>
        <div><small>Event date</small><strong>{dateLabel(item.date)}</strong></div>
        <div><small>Venue</small><strong>{item.venue || "—"}</strong></div>
        <div><small>Request ID</small><strong>#{item.id}</strong></div>
      </div>
      <div className="request-note"><small>YOUR REASON</small><p>{item.reason}</p></div>
      <h3>Approval journey</h3>
      <div className="journey">
        <div className="done"><i><Icon name="check" size={14} /></i><span><strong>Request submitted</strong><small>{submittedLabel(item.created_at)}</small></span></div>
        {item.event_type === "open" ? (
          <div className="done"><i><Icon name="check" size={14} /></i><span><strong>Coordinator step skipped</strong><small>Open events go directly to your teacher</small></span></div>
        ) : (
          <div className={coordinatorReviewed ? "done" : "current"}><i><Icon name={coordinatorReviewed ? "check" : "clock"} size={14} /></i><span><strong>Coordinator review</strong><small>{coordinatorReviewed ? item.coordinator_remarks || "Decision recorded" : "Waiting for review"}</small></span></div>
        )}
        <div className={teacherReviewed ? (item.status === "teacher_rejected" ? "current" : "done") : "current"}><i><Icon name={teacherReviewed && !rejected ? "check" : "clock"} size={14} /></i><span><strong>Teacher review</strong><small>{teacherReviewed ? item.teacher_remarks || (rejected ? "Request rejected" : "Approved") : "Final attendance approval"}</small></span></div>
        {item.attendance && <div className="done"><i><Icon name="check" size={14} /></i><span><strong>Attendance marked</strong><small>Event participation confirmed</small></span></div>}
      </div>
    </div>
  )
}

function StudentDashboard({ user, data, filter, onFilter, onRefresh, onSuccess }: CommonProps) {
  const [newOpen, setNewOpen] = useState(false)
  const [selected, setSelected] = useState<AttendanceRequest | null>(null)
  const [sending, setSending] = useState(false)
  return (
    <div className="dashboard student-theme">
      <section className="student-hero">
        <div className="hero-copy"><span className="eyebrow dark"><Icon name="spark" size={14} /> YOUR ATTENDANCE HQ</span>
          <h1>Hey {user.full_name.split(" ")[0]}, make it<br />count<span>.</span></h1>
          <p>Big events. Zero attendance stress. Track every request from send to signed-off.</p>
          <button className="primary-btn lime" onClick={() => setNewOpen(true)}><Icon name="plus" />New request <Icon name="arrow" /></button>
        </div>
        <div className="hero-art" aria-hidden="true"><div className="orbit orbit-one" /><div className="orbit orbit-two" /><div className="pass-card"><span className="mini-label">NEXT UP</span><strong>EVENT<br />PASS</strong><div><span>ATTENDEE</span><span>READY</span></div><i>TRACK YOUR APPROVAL</i></div><span className="sticker sticker-one">GO<br />FOR IT</span><span className="sticker sticker-two"><Icon name="spark" size={28} /></span></div>
      </section>
      <section className="metrics-grid student-metrics">
        <Metric label="Total requests" value={data.stats.total || 0} note="All submissions" icon="file" tone="purple" />
        <Metric label="Pending" value={data.stats.pending || 0} note="Coordinator review" icon="clock" tone="amber" />
        <Metric label="In progress" value={data.stats.in_progress || 0} note="Teacher review" icon="arrow" tone="blue" />
        <Metric label="Approved" value={data.stats.approved || 0} note="You're all set" icon="check" tone="green" />
        <Metric label="Rejected" value={data.stats.rejected || 0} note="Review decision" icon="x" tone="red" />
      </section>
      <section className="panel">
        <div className="panel-header"><div><span className="eyebrow">YOUR TIMELINE</span><h2>Recent requests</h2></div><FilterPills items={[{ label: "All", value: "" }, { label: "Pending", value: "pending" }, { label: "In Progress", value: "in_progress" }, { label: "Approved", value: "approved" }, { label: "Rejected", value: "rejected" }]} active={filter} onChange={onFilter} /></div>
        {data.requests.length ? <DataTable headers={["Event", "Type", "Event date", "Status", "Submitted", ""]}>{data.requests.map((row) => <tr key={row.id}>
          <td><div className="event-cell"><span>{row.event.slice(0, 2).toUpperCase()}</span><div><strong>{row.event}</strong><small>{row.event_type_label}</small></div></div></td>
          <td><span className="type-tag">{row.event_type === "open" && <Icon name="external" size={13} />}{row.event_type_label}</span></td>
          <td>{dateLabel(row.date)}</td><td><Status value={statusText(row, "student")} /></td><td className="muted">{submittedLabel(row.created_at)}</td>
          <td><button className="text-btn" onClick={() => setSelected(row)}>View <Icon name="chevron" size={14} /></button></td>
        </tr>)}</DataTable> : <EmptyPanel message={filter ? "No requests match this filter." : "Submit your first event attendance request to get started."} />}
        <div className="panel-footer"><span>Showing {data.requests.length} requests</span><button onClick={onRefresh}>Refresh <Icon name="arrow" size={15} /></button></div>
      </section>
      {newOpen && <Modal title="Create a new request" close={() => setNewOpen(false)}><RequestForm events={data.events || []} close={() => setNewOpen(false)} onSubmit={async (payload) => { setSending(true); try { await api.createRequest(payload); await onSuccess("Attendance request submitted."); } finally { setSending(false); } }} /></Modal>}
      {selected && <Modal title={selected.event} close={() => setSelected(null)}><RequestDetail item={selected} role="student" /></Modal>}
      {sending && <span className="sr-only" role="status">Submitting request</span>}
    </div>
  )
}

function ReviewPanel({ request, teacher, close, onReview }: {
  request: AttendanceRequest
  teacher: boolean
  close: () => void
  onReview: (id: number, action: "approve" | "reject", remarks: string) => Promise<void>
}) {
  const [remarks, setRemarks] = useState("")
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState("")
  async function decide(action: "approve" | "reject") {
    setSaving(true)
    setError("")
    try {
      await onReview(request.id, action, remarks)
      close()
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not save your decision.")
    } finally {
      setSaving(false)
    }
  }
  return (
    <div className="form-body">
      <div className="review-summary"><span className="avatar large">{initials(request.student.name)}</span><div><strong>{request.student.name}</strong><small>{request.event} · {dateLabel(request.date)}</small></div></div>
      <div className="request-note"><small>STUDENT’S REASON</small><p>{request.reason}</p></div>
      <label htmlFor="review-remarks">Reviewer remarks <span>(optional)</span></label><textarea id="review-remarks" rows={3} value={remarks} onChange={(event) => setRemarks(event.target.value)} placeholder="Add a note for the student…" />
      <div className="decision-note"><Icon name="file" /><span><strong>{teacher ? "Final approval stage" : "Coordinator review"}</strong><small>{teacher ? "Your decision will complete the approval flow." : "Approved requests move to the class teacher."}</small></span></div>
      {error && <p className="form-error" role="alert">{error}</p>}
      <div className="modal-actions split"><button className="reject-btn" type="button" disabled={saving} onClick={() => void decide("reject")}><Icon name="x" />{saving ? "Saving…" : "Reject"}</button><button className="approve-btn" type="button" disabled={saving} onClick={() => void decide("approve")}><Icon name="check" />Approve request</button></div>
    </div>
  )
}

function EventForm({ close, onSuccess }: { close: () => void; onSuccess: (payload: Record<string, string | boolean>) => Promise<void> }) {
  const [name, setName] = useState("")
  const [date, setDate] = useState("")
  const [time, setTime] = useState("")
  const [venue, setVenue] = useState("")
  const [description, setDescription] = useState("")
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState("")
  async function submit(event: FormEvent) {
    event.preventDefault()
    setSaving(true)
    setError("")
    try {
      await onSuccess({ name, date, time, venue, description, is_active: true })
      close()
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not create this event.")
    } finally {
      setSaving(false)
    }
  }
  return (
    <form className="form-body" onSubmit={submit}>
      <div className="field-grid"><div><label htmlFor="event-name">Event name</label><input id="event-name" required value={name} onChange={(event) => setName(event.target.value)} placeholder="e.g. TechVista" /></div><div><label htmlFor="event-date">Event date</label><input id="event-date" required type="date" value={date} onChange={(event) => setDate(event.target.value)} /></div></div>
      <div className="field-grid"><div><label htmlFor="event-time">Start time</label><input id="event-time" required type="time" value={time} onChange={(event) => setTime(event.target.value)} /></div><div><label htmlFor="event-venue">Venue</label><input id="event-venue" required value={venue} onChange={(event) => setVenue(event.target.value)} placeholder="Campus venue" /></div></div>
      <div><label htmlFor="event-description">Event description</label><textarea id="event-description" required rows={4} value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Add a short description for students…" /></div>
      {error && <p className="form-error" role="alert">{error}</p>}
      <div className="modal-actions"><button className="secondary-btn" type="button" onClick={close}>Cancel</button><button className="primary-btn" disabled={saving}>{saving ? "Publishing…" : "Publish event"} <Icon name="arrow" /></button></div>
    </form>
  )
}

function CoordinatorDashboard({ user, data, filter, onFilter, onRefresh, onSuccess }: CommonProps) {
  const [review, setReview] = useState<AttendanceRequest | null>(null)
  const [create, setCreate] = useState(false)
  const [saving, setSaving] = useState(false)
  const avgCount = data.stats.total || 0
  return (
    <div className="dashboard pro-theme">
      <section className="welcome-row"><div><span className="eyebrow">EVENT OPERATIONS</span><h1>Welcome, {user.full_name}.</h1><p>Review and manage attendance requests for your events.</p></div><button className="primary-btn" onClick={() => setCreate(true)}><Icon name="plus" />Create event</button></section>
      <section className="insight-banner"><div className="insight-icon"><Icon name="spark" /></div><div><span>TODAY’S PULSE</span><strong>{data.stats.pending || 0} requests need a decision</strong><p>Requests shown here are for events you organize.</p></div><div className="pulse-bars">{[35, 55, 45, 72, 62, 90, 75].map((height, index) => <i style={{ height: `${height}%` }} key={index} />)}</div></section>
      <section className="metrics-grid four">
        <Metric label="Pending review" value={data.stats.pending || 0} note="Needs your action" icon="clock" tone="amber" />
        <Metric label="Approved" value={data.stats.approved || 0} note="Requests approved" icon="check" tone="green" />
        <Metric label="Rejected" value={data.stats.rejected || 0} note="Requests declined" icon="x" tone="red" />
        <Metric label="Total requests" value={avgCount} note="Across your events" icon="file" tone="blue" />
      </section>
      <section className="panel">
        <div className="panel-header"><div><span className="eyebrow">FIRST-STAGE REVIEW</span><h2>Event requests</h2></div><FilterPills items={[{ label: "All Active", value: "" }, { label: "Pending", value: "pending" }, { label: "Approved", value: "approved" }, { label: "Rejected", value: "rejected" }]} active={filter} onChange={onFilter} /></div>
        {data.requests.length ? <DataTable headers={["Student", "Department", "Event & date", "Reason", "Status", "Submitted", ""]}>{data.requests.map((row) => <tr key={row.id}>
          <td><div className="person-cell"><span>{initials(row.student.name)}</span><div><strong>{row.student.name}</strong><small>{row.student.division || "Division not assigned"}</small></div></div></td>
          <td>{row.student.department || "—"}</td><td><strong>{row.event}</strong><small className="block">{dateLabel(row.date)}</small></td><td className="muted">{row.reason}</td><td><Status value={statusText(row, "coordinator")} /></td><td className="muted">{submittedLabel(row.created_at)}</td>
          <td>{row.status === "pending" ? <button className="review-btn" onClick={() => setReview(row)}>Review <Icon name="arrow" size={14} /></button> : <span className="reviewed"><Icon name="check" size={14} />Reviewed</span>}</td>
        </tr>)}</DataTable> : <EmptyPanel message={filter ? "No requests match this filter." : "Student requests for your events will appear here."} />}
        <div className="panel-footer"><span>Showing {data.requests.length} requests</span><button onClick={onRefresh}>Refresh <Icon name="arrow" size={15} /></button></div>
      </section>
      <section className="panel activity-panel"><div className="panel-header"><div><span className="eyebrow">YOUR EVENTS</span><h2>Managed events</h2></div></div>
        {data.events?.length ? <div className="activity-grid">{data.events.map((event, index) => <div className="activity-card" key={event.id}><div className="activity-rank">0{index + 1}</div><div className="person-cell"><span><Icon name="calendar" size={16} /></span><div><strong>{event.name}</strong><small>{dateLabel(event.date)} · {event.time}</small></div></div><div className="event-venue">{event.venue}</div></div>)}</div> : <EmptyPanel message="Create an event to make it available for student requests." />}
      </section>
      {review && <Modal title="Review attendance request" close={() => setReview(null)}><ReviewPanel request={review} teacher={false} close={() => setReview(null)} onReview={async (id, action, remarks) => { await api.reviewRequest(id, action, remarks); await onSuccess(`Request ${action === "approve" ? "approved" : "rejected"}.`); }} /></Modal>}
      {create && <Modal title="Create a new event" close={() => setCreate(false)}><EventForm close={() => setCreate(false)} onSuccess={async (payload) => { setSaving(true); try { await api.createEvent(payload); await onSuccess("Event created successfully."); } finally { setSaving(false); } }} /></Modal>}
      {saving && <span className="sr-only" role="status">Saving event</span>}
    </div>
  )
}

function TeacherDashboard({ user, data, filter, onFilter, onRefresh, onSuccess, month, onMonth }: CommonProps & {
  month: string
  onMonth: (month: string) => void
}) {
  const [review, setReview] = useState<AttendanceRequest | null>(null)
  const [busyId, setBusyId] = useState<number | null>(null)
  const [actionError, setActionError] = useState("")
  const activity = data.student_activity || []
  const approved = data.stats.approved || 0
  const rejected = data.stats.rejected || 0
  const approvalRate = approved + rejected ? Math.round((approved / (approved + rejected)) * 100) : 0
  const months = [{ value: "", label: "All months" }, ...Array.from({ length: 12 }, (_, index) => ({ value: String(index + 1), label: new Intl.DateTimeFormat("en", { month: "long" }).format(new Date(2024, index, 1)) }))]
  async function exportExcel() {
    const params = new URLSearchParams()
    if (month) params.set("month", month)
    window.location.assign(`/attendance/teacher/export/excel/${params.size ? `?${params}` : ""}`)
  }
  return (
    <div className="dashboard teacher-theme">
      <section className="welcome-row teacher-welcome"><div><span className="division-chip"><Icon name="users" size={15} />{data.teacher_division || user.division || "Division not assigned"}</span><h1>Class overview</h1><p>Final approvals and attendance for your division.</p></div>
        <div className="header-actions"><label className="month-select"><Icon name="calendar" /><select aria-label="Filter by submission month" value={month} onChange={(event) => onMonth(event.target.value)}>{months.map((item) => <option key={item.value || "all"} value={item.value}>{item.label}</option>)}</select></label><button className="secondary-btn export" onClick={() => void exportExcel()}><Icon name="download" />Export Excel</button></div>
      </section>
      <section className="teacher-summary"><div className="ring-wrap"><div className="progress-ring" style={{ background: `conic-gradient(#8edcff 0 ${approvalRate}%, #42577a ${approvalRate}% 100%)` }}><span><b>{approvalRate}%</b><small>Approval rate</small></span></div><div><span className="eyebrow">DIVISION HEALTH</span><h3>Student attendance overview</h3><p>{activity.length} students have submitted event requests{month ? " in the selected month" : ""}.</p></div></div>
        <div className="compact-metrics"><div><span className="dot amber" /><b>{String(data.stats.awaiting || 0).padStart(2, "0")}</b><small>Awaiting</small></div><div><span className="dot green" /><b>{String(approved).padStart(2, "0")}</b><small>Approved</small></div><div><span className="dot red" /><b>{String(rejected).padStart(2, "0")}</b><small>Rejected</small></div><div><span className="dot teal" /><b>{String(data.stats.attended || 0).padStart(2, "0")}</b><small>Attended</small></div></div>
      </section>
      <section className="metrics-grid four">
        <Metric label="Awaiting review" value={data.stats.awaiting || 0} note="Coordinator-approved" icon="clock" tone="amber" />
        <Metric label="Approved" value={approved} note="Teacher-approved" icon="check" tone="green" />
        <Metric label="Rejected" value={rejected} note="Teacher decisions" icon="x" tone="red" />
        <Metric label="Attended" value={data.stats.attended || 0} note="Verified attendance" icon="users" tone="blue" />
      </section>
      <section className="panel"><div className="panel-header"><div><span className="eyebrow">FINAL DECISIONS</span><h2>Approval queue</h2></div><FilterPills items={[{ label: "All Active", value: "" }, { label: "Awaiting", value: "awaiting" }, { label: "Approved", value: "approved" }, { label: "Rejected", value: "teacher_rejected" }]} active={filter} onChange={onFilter} /></div>
        {actionError && <p className="state-banner state-error" role="alert">{actionError}</p>}
        {data.requests.length ? <DataTable headers={["Student", "Event", "Type", "Coordinator", "Status", "Attendance", ""]}>{data.requests.map((row) => <tr key={row.id}>
          <td><div className="person-cell"><span>{initials(row.student.name)}</span><div><strong>{row.student.name}</strong><small>{row.student.student_id || "No roll number"} · {row.student.division}</small></div></div></td>
          <td><strong>{row.event}</strong><small className="block">{dateLabel(row.date)} · {row.venue}</small></td><td><span className="type-tag">{row.event_type_label}</span></td><td>{row.coordinator || "Direct to teacher"}</td><td><Status value={statusText(row, "teacher")} /></td>
          <td>{row.attendance ? <Status value="Attended" /> : row.status === "teacher_approved" ? <button className="mark-btn" disabled={busyId === row.id} onClick={async () => { setBusyId(row.id); setActionError(""); try { await api.markAttendance(row.id); await onSuccess("Attendance marked."); } catch (cause) { setActionError(cause instanceof Error ? cause.message : "Could not mark attendance."); } finally { setBusyId(null); } }}><Icon name="check" size={14} />{busyId === row.id ? "Saving…" : "Mark attended"}</button> : <span className="muted">Not available</span>}</td>
          <td>{row.status === "coordinator_approved" ? <button className="review-btn" onClick={() => setReview(row)}>Review <Icon name="arrow" size={14} /></button> : <span className="reviewed">{row.status === "teacher_approved" || row.status === "teacher_rejected" ? "Reviewed" : "—"}</span>}</td>
        </tr>)}</DataTable> : <EmptyPanel message={filter ? "No requests match this filter." : "Coordinator-approved requests for your division will appear here."} />}
        <div className="panel-footer"><span>Showing {data.requests.length} requests</span><button onClick={onRefresh}>Refresh <Icon name="arrow" size={15} /></button></div>
      </section>
      <section className="panel activity-panel"><div className="panel-header"><div><span className="eyebrow">DIVISION INSIGHTS</span><h2>Student activity</h2></div></div>
        {activity.length ? <div className="activity-grid">{activity.map((student: StudentActivity, index) => <div className="activity-card" key={student.id}><div className="activity-rank">{String(index + 1).padStart(2, "0")}</div><div className="person-cell"><span>{initials(`${student.first_name} ${student.last_name}`.trim() || student.username)}</span><div><strong>{`${student.first_name} ${student.last_name}`.trim() || student.username}</strong><small>{student.student_id || "No roll number"}</small></div></div><div className="activity-stats"><span><b>{student.total}</b>Total</span><span><b>{student.pending}</b>Pending</span><span><b>{student.approved}</b>Approved</span><span><b>{student.rejected}</b>Rejected</span></div></div>)}</div> : <EmptyPanel message="Students who submit attendance requests will appear here." />}
      </section>
      {review && <Modal title="Final approval decision" close={() => setReview(null)}><ReviewPanel request={review} teacher close={() => setReview(null)} onReview={async (id, action, remarks) => { await api.reviewRequest(id, action, remarks); await onSuccess(`Request ${action === "approve" ? "approved" : "rejected"}.`); }} /></Modal>}
    </div>
  )
}

export { StudentDashboard, CoordinatorDashboard, TeacherDashboard }
