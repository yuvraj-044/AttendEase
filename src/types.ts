export type Role = "student" | "coordinator" | "teacher"

export interface User {
  id: number
  role: Role
  role_label: string
  full_name: string
  username: string
  email: string
  department: string
  division: string
  grade: string
  student_id: string
}

export interface EventItem {
  id: number
  name: string
  description?: string
  date: string
  time: string
  venue: string
  organizer?: string
}

export interface AttendanceRequest {
  id: number
  event: string
  event_type: "coordinator" | "open"
  event_type_label: string
  date: string
  time: string
  venue: string
  reason: string
  status: string
  status_label: string
  created_at: string
  student: {
    id: number
    name: string
    username: string
    department: string
    division: string
    student_id: string
  }
  coordinator: string
  attendance: boolean
  coordinator_remarks: string
  teacher_remarks: string
}

export interface StudentActivity {
  id: number
  first_name: string
  last_name: string
  username: string
  student_id: string
  total: number
  pending: number
  approved: number
  rejected: number
}

export interface DashboardData {
  stats: Record<string, number>
  requests: AttendanceRequest[]
  events?: EventItem[]
  student_activity?: StudentActivity[]
  teacher_division?: string
  month?: string
}
