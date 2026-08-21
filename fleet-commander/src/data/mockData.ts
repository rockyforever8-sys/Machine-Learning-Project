import type { Robot, Task } from '../types'

export const initialRobots: Robot[] = [
  { id: 'r1', name: 'Atlas-01', battery: 87, location: 'Zone A — Bay 3', status: 'working', color: '#2563eb', taskIds: ['t1', 't4'], arenaX: 18, arenaY: 22 },
  { id: 'r2', name: 'Nova-02', battery: 62, location: 'Zone B — Corridor 7', status: 'working', color: '#7c3aed', taskIds: ['t2'], arenaX: 50, arenaY: 15 },
  { id: 'r3', name: 'Pulse-03', battery: 94, location: 'Zone A — Dock 1', status: 'idle', color: '#0891b2', taskIds: [], arenaX: 82, arenaY: 22 },
  { id: 'r4', name: 'Spark-04', battery: 41, location: 'Zone C — Storage', status: 'working', color: '#059669', taskIds: ['t3', 't5'], arenaX: 25, arenaY: 72 },
  { id: 'r5', name: 'Bolt-05', battery: 28, location: 'Charging Station 2', status: 'charging', color: '#d97706', taskIds: [], arenaX: 50, arenaY: 78 },
  { id: 'r6', name: 'Echo-06', battery: 73, location: 'Zone D — Lab 4', status: 'working', color: '#dc2626', taskIds: ['t6'], arenaX: 75, arenaY: 72 },
]

export const initialTasks: Task[] = [
  { id: 't1', title: 'Inventory Scan — Shelf A12', duration: 45, progress: 72, priority: 'high', assignedRobotId: 'r1', startOffset: 0 },
  { id: 't2', title: 'Package Delivery — Dock 7', duration: 30, progress: 35, priority: 'medium', assignedRobotId: 'r2', startOffset: 0 },
  { id: 't3', title: 'Pallet Relocation — Row 5', duration: 60, progress: 18, priority: 'high', assignedRobotId: 'r4', startOffset: 0 },
  { id: 't4', title: 'Sensor Calibration', duration: 20, progress: 0, priority: 'low', assignedRobotId: 'r1', startOffset: 50 },
  { id: 't5', title: 'Quality Inspection — Lot 88', duration: 40, progress: 55, priority: 'medium', assignedRobotId: 'r4', startOffset: 65 },
  { id: 't6', title: 'Data Collection — Lab Run', duration: 25, progress: 90, priority: 'low', assignedRobotId: 'r6', startOffset: 0 },
  { id: 't7', title: 'Route Mapping — Zone E', duration: 50, progress: 0, priority: 'medium', assignedRobotId: null, startOffset: 0 },
  { id: 't8', title: 'Maintenance Check — Arm Joint', duration: 15, progress: 0, priority: 'high', assignedRobotId: null, startOffset: 0 },
  { id: 't9', title: 'Waste Collection — Floor 2', duration: 35, progress: 0, priority: 'low', assignedRobotId: null, startOffset: 0 },
]
