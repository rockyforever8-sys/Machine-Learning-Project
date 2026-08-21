import {
  DndContext,
  DragOverlay,
  PointerSensor,
  TouchSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragStartEvent,
} from '@dnd-kit/core'
import { useState } from 'react'
import { Toaster } from 'sonner'
import { Bot, Share2 } from 'lucide-react'
import { useFleetState } from './hooks/useFleetState'
import { TaskList } from './components/TaskList'
import { RobotCard } from './components/RobotCard'
import { FleetArena } from './components/FleetArena'
import { WaterfallTimeline } from './components/WaterfallTimeline'
import { RobotVitalsPanel } from './components/RobotVitalsPanel'
import { TaskCard } from './components/TaskCard'
import type { Task } from './types'

function App() {
  const {
    robots,
    tasks,
    selectedRobotId,
    selectedRobot,
    unassignedTasks,
    setSelectedRobotId,
    assignTask,
  } = useFleetState()

  const [activeTask, setActiveTask] = useState<Task | null>(null)
  const [activeTab, setActiveTab] = useState<'fleet' | 'waterfall'>('fleet')

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
    useSensor(TouchSensor, { activationConstraint: { delay: 200, tolerance: 5 } }),
  )

  const handleDragStart = (event: DragStartEvent) => {
    const task = event.active.data.current?.task as Task | undefined
    if (task) setActiveTask(task)
  }

  const handleDragEnd = (event: DragEndEvent) => {
    setActiveTask(null)
    const { active, over } = event
    if (!over) return

    const taskId = (active.data.current?.task as Task)?.id ?? active.id.toString().replace('waterfall-task-', '')
    const overData = over.data.current

    if (overData?.type === 'robot' && overData.robotId) {
      const task = tasks.find(t => t.id === taskId)
      if (task && task.assignedRobotId !== overData.robotId) {
        assignTask(taskId, overData.robotId)
      }
    }
  }

  const handleShare = async () => {
    const url = window.location.href
    if (navigator.share) {
      try {
        await navigator.share({ title: 'Digital Twin Task Commander', url })
      } catch { /* user cancelled */ }
    } else {
      await navigator.clipboard.writeText(url)
      alert('Link copied to clipboard!')
    }
  }

  return (
    <DndContext sensors={sensors} onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
      <div className="min-h-full flex flex-col bg-surface">
        <Toaster position="top-center" richColors closeButton />

        <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-gray-200 px-4 py-3">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="p-2 bg-accent/10 rounded-xl">
                <Bot className="w-5 h-5 text-accent" />
              </div>
              <div>
                <h1 className="text-base sm:text-lg font-bold text-gray-900 leading-tight">
                  Digital Twin Commander
                </h1>
                <p className="text-[10px] sm:text-xs text-gray-500">Fleet Task Management</p>
              </div>
            </div>
            <button
              onClick={handleShare}
              className="flex items-center gap-1.5 px-3 py-2 bg-accent text-white rounded-xl text-xs sm:text-sm font-medium hover:bg-accent-dark transition-colors"
            >
              <Share2 className="w-4 h-4" />
              <span className="hidden sm:inline">Share</span>
            </button>
          </div>
        </header>

        <main className="flex-1 max-w-7xl mx-auto w-full p-4 space-y-4">
          <FleetArena
            robots={robots}
            selectedRobotId={selectedRobotId}
            onSelectRobot={setSelectedRobotId}
          />

          <div className="flex gap-2">
            {(['fleet', 'waterfall'] as const).map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`
                  flex-1 py-2 rounded-xl text-sm font-medium transition-colors
                  ${activeTab === tab
                    ? 'bg-accent text-white'
                    : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'}
                `}
              >
                {tab === 'fleet' ? 'Robot Cards' : 'Waterfall View'}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
            <div className="lg:col-span-4 bg-white rounded-2xl border border-gray-200 p-4 min-h-[300px] lg:min-h-[400px]">
              <TaskList tasks={unassignedTasks} />
            </div>

            <div className="lg:col-span-8">
              {activeTab === 'fleet' ? (
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {robots.map(robot => (
                    <RobotCard
                      key={robot.id}
                      robot={robot}
                      tasks={tasks}
                      selected={selectedRobotId === robot.id}
                      onSelect={() => setSelectedRobotId(robot.id)}
                    />
                  ))}
                </div>
              ) : (
                <WaterfallTimeline robots={robots} tasks={tasks} />
              )}
            </div>
          </div>
        </main>

        {selectedRobot && (
          <RobotVitalsPanel
            robot={selectedRobot}
            tasks={tasks}
            onClose={() => setSelectedRobotId(null)}
          />
        )}
      </div>

      <DragOverlay>
        {activeTask ? (
          <div className="rotate-2 scale-105">
            <TaskCard task={activeTask} />
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  )
}

export default App
