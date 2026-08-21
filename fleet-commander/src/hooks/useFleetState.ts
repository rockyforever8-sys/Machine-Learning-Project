import { useState, useCallback } from 'react'
import { toast } from 'sonner'
import type { Robot, Task, AssignmentLog } from '../types'
import { initialRobots, initialTasks } from '../data/mockData'

export function useFleetState() {
  const [robots, setRobots] = useState<Robot[]>(initialRobots)
  const [tasks, setTasks] = useState<Task[]>(initialTasks)
  const [selectedRobotId, setSelectedRobotId] = useState<string | null>(null)
  const [assignmentLogs, setAssignmentLogs] = useState<AssignmentLog[]>([])

  const assignTask = useCallback((taskId: string, toRobotId: string) => {
    const task = tasks.find(t => t.id === taskId)
    const toRobot = robots.find(r => r.id === toRobotId)
    if (!task || !toRobot) return

    const fromRobotId = task.assignedRobotId

    setTasks(prev =>
      prev.map(t =>
        t.id === taskId ? { ...t, assignedRobotId: toRobotId, progress: t.progress } : t
      )
    )

    setRobots(prev =>
      prev.map(r => {
        if (r.id === fromRobotId) {
          return { ...r, taskIds: r.taskIds.filter(id => id !== taskId) }
        }
        if (r.id === toRobotId && !r.taskIds.includes(taskId)) {
          return { ...r, taskIds: [...r.taskIds, taskId], status: r.status === 'charging' ? 'charging' : 'working' }
        }
        return r
      })
    )

    const log: AssignmentLog = {
      id: `log-${Date.now()}`,
      taskId,
      taskTitle: task.title,
      fromRobotId,
      toRobotId,
      toRobotName: toRobot.name,
      timestamp: new Date(),
    }
    setAssignmentLogs(prev => [log, ...prev])

    toast.success(`"${task.title}" assigned to ${toRobot.name}`, {
      description: fromRobotId
        ? `Reassigned from ${robots.find(r => r.id === fromRobotId)?.name}`
        : 'New assignment from task pool',
      duration: 3000,
    })
  }, [tasks, robots])

  const unassignTask = useCallback((taskId: string) => {
    const task = tasks.find(t => t.id === taskId)
    if (!task || !task.assignedRobotId) return

    const fromRobotId = task.assignedRobotId

    setTasks(prev =>
      prev.map(t => (t.id === taskId ? { ...t, assignedRobotId: null } : t))
    )

    setRobots(prev =>
      prev.map(r =>
        r.id === fromRobotId
          ? { ...r, taskIds: r.taskIds.filter(id => id !== taskId) }
          : r
      )
    )
  }, [tasks])

  const selectedRobot = robots.find(r => r.id === selectedRobotId) ?? null
  const unassignedTasks = tasks.filter(t => !t.assignedRobotId)

  return {
    robots,
    tasks,
    selectedRobotId,
    selectedRobot,
    assignmentLogs,
    unassignedTasks,
    setSelectedRobotId,
    assignTask,
    unassignTask,
  }
}
