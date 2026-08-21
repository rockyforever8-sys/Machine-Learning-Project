import { TaskCard } from './TaskCard'
import type { Task } from '../types'
import { ListTodo } from 'lucide-react'

interface TaskListProps {
  tasks: Task[]
}

export function TaskList({ tasks }: TaskListProps) {
  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 mb-3 px-1">
        <ListTodo className="w-5 h-5 text-accent" />
        <h2 className="text-base font-semibold text-gray-800">Task Pool</h2>
        <span className="ml-auto text-xs bg-accent/10 text-accent px-2 py-0.5 rounded-full font-medium">
          {tasks.length}
        </span>
      </div>

      <p className="text-xs text-gray-500 mb-3 px-1">
        Drag tasks onto a robot to assign
      </p>

      <div className="flex-1 overflow-y-auto space-y-2 pr-1 -mr-1">
        {tasks.length === 0 ? (
          <div className="text-center py-8 text-gray-400 text-sm">
            All tasks assigned
          </div>
        ) : (
          tasks.map(task => <TaskCard key={task.id} task={task} />)
        )}
      </div>
    </div>
  )
}
