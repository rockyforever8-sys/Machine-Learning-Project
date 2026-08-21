export type RobotStatus = 'idle' | 'working' | 'charging' | 'error'
export type TaskPriority = 'low' | 'medium' | 'high'

export interface Task {
  id: string
  title: string
  duration: number
  progress: number
  priority: TaskPriority
  assignedRobotId: string | null
  startOffset: number
}

export interface Robot {
  id: string
  name: string
  battery: number
  location: string
  status: RobotStatus
  color: string
  taskIds: string[]
  arenaX: number
  arenaY: number
}

export interface AssignmentLog {
  id: string
  taskId: string
  taskTitle: string
  fromRobotId: string | null
  toRobotId: string
  toRobotName: string
  timestamp: Date
}
