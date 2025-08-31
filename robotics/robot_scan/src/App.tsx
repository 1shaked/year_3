import { useState } from 'react'
import reactLogo from './assets/react.svg'
import './App.css'
import { useFieldArray, useForm } from 'react-hook-form'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="App">
      <SetUp />
    </div>
  )
}

function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
function toNumber(v: string | number) {
  return typeof v === 'string' ? parseFloat(v) : v
}
interface SetUpFormI {
  M: number, // x axis
  N: number, // y axis
  obstacles: {x: number, y: number}[],
}

const leftPush = {
  '14': '-0px',
  '13': '-22px',
  '12': '-44px',
  '11': '-66px',
  '10': '-90px',
  '9': '-111px',
  '8': '-132px',
  '7': '-155px',
  '6': '-180px',
  '5': '-200px',
}

export function SetUp() {
  const form = useForm<SetUpFormI>({
    defaultValues: { M: 8, obstacles: [ { x: 1, y: 4 } , { x: 2, y: 1 }, { x: 5, y: 2 } , { x: 6, y: 7 } ] }
  })
  const obstacles = useFieldArray({
    control: form.control,
    name: "obstacles"
  })
  const M = form.watch("M")
  // const N = form.watch("N")
  const N = M

  const [obstaclesState, setObstaclesState] = useState<{x: number, y: number}[]>([])
  const [blueCells, setBlueCells] = useState<{x: number, y: number}[]>([])

  const [obstaclesEncountered, setObstaclesEncountered] = useState<{x: number, y: number} | null>(null)
  async function runAlgorithm() {
    // placeholder for running the algorithm
    // color the first cell blue
    const start = { x: 0, y: 0 } as const
    // let location = start
    const markedCells: {x: number, y: number}[] = []
    for ( let i = 0; i < M; i++ ) {
      // color all the x values from (i,0) to the obstacles or the end of the grid
      const blueCells: {x: number, y: number}[] = [{ x: i, y: 0 }]
      // debugger
      for ( let j = 0; j < N; j++ ) {
        let cell = { x: i, y: j }
        if ( obstaclesState.some(ob => ob.x === cell.x && ob.y === cell.y) && !markedCells.some(mc => mc.x === cell.x && mc.y === cell.y) ) {
          // color the cell blue
          setBlueCells(_ => [...blueCells] )
          // remove the obstacle cell from the obstacles
          setObstaclesState(prev => [...prev.filter(ob => ob.x !== cell.x || ob.y !== cell.y)])
          await sleep(1000)
          setObstaclesEncountered(cell)
          setBlueCells(_ => [] )
          console.log('obstaclesState after removal: ', obstaclesState)
          console.log(`Encountered an obstacle at (${cell.x}, ${cell.y}). Stopping the scan in this column. And returning home.`)
          markedCells.push({x: cell.x, y: cell.y})
          i = i - 1
          await sleep(1000)
          setObstaclesEncountered(null)
          break
        }
        blueCells.push(cell)
      }
      // color the cell blue
      setBlueCells(_ => [...blueCells] )
      await sleep(1200)
    }
    setBlueCells([])
    console.log('Finished scanning the grid.')
    console.log('Remaining obstacles: ', obstaclesState)
  }
  return (
    <div>
      <h2>
        Robotic Project by Noam & Shaked
      </h2>
      <h1>Set Up Your Environment</h1>
      <form onSubmit={form.handleSubmit((data) => {
        console.log(data)
        
        setObstaclesState(data.obstacles.map(obj => ({ x: toNumber(obj.x), y: toNumber(obj.y) })))
      })}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <label style={{ fontSize: '1.2em', fontWeight: 'bold' }}>Grid Size</label>
          <input type="number" {...form.register("M")} style={{ width: '60px', fontSize: '1.6em' }} placeholder='Grid Size' />
        </div>
        <h3>Obstacles</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', marginBottom: '10px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
            <span style={{ fontWeight: 'bold', marginRight: '10px' }}>X</span>
            <span style={{ fontWeight: 'bold', marginRight: '10px' }}>Y</span>
            <span style={{ fontWeight: 'bold' }}></span>
          </div>
          {obstacles.fields.map((field, index) => (
            <div key={field.id} style={{ display: 'flex', gap: '5px', alignItems: 'center', justifyContent: 'space-between' }}>
              <input type="number" {...form.register(`obstacles.${index}.x`)} style={{ width: '60px' , fontSize: '1.3em' }} />
              <input type="number" {...form.register(`obstacles.${index}.y`)} style={{ width: '60px' , fontSize: '1.3em' }} />
              <button type="button" onClick={() => obstacles.remove(index)} style={{ background: '#ff4d4f', color: 'white', border: 'none', borderRadius: '4px', padding: '5px 10px' }}>Remove</button>
            </div>
          ))}
        </div>
        <button type="button" onClick={() => obstacles.append({ x: 0, y: 0 })} style={{ background: '#4CAF50', color: 'white', border: 'none', borderRadius: '4px', padding: '5px 10px' }}>Add Obstacle</button>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px' }}>
          <button type="submit" style={{ background: '#eadcdcff', color: 'black', border: 'none', borderRadius: '4px', padding: '5px 10px' }}>Insert params</button>
          <button type='button' onClick={() => {
            runAlgorithm()
          }} style={{ background: '#2196F3', color: 'white', border: 'none', borderRadius: '4px', padding: '5px 10px', }}>Run algorithm</button>
        </div>
        {/* display the grid */}
        <div style={{ display: 'grid', gridTemplateColumns: `repeat(${M}, 40px)`, gap: '2px', marginTop: '20px', position: 'relative' }}>
          {/* Draw all the rows in the grid */}
          <svg style={{ position: 'absolute', top: '0', left: `${M.toString() in leftPush ? leftPush[M.toString() as keyof typeof leftPush] : '100px'}`, width: '100%', height: '100%' }} viewBox={`0 0 ${M * 40} ${N * 40}`} xmlns="http://www.w3.org/2000/svg">
            <line x1="0" y1="0" y2={`${obstaclesEncountered ? obstaclesEncountered.x * 40 : 0}`} x2={`${obstaclesEncountered ? obstaclesEncountered.y * 40 : 0}`} stroke="green" strokeWidth={4} 
            style={{
              opacity: obstaclesEncountered ? 1 : 0,
              transition: 'all 0.5s ease',
              // strokeDasharray: 100,
              // strokeDashoffset: 100,
              animation: "draw 0.2s linear forwards"
            }}/>
          </svg>
          {/* {obstaclesEncountered ? 
            // <AnimatedLine x1={0} y1={0} x2={obstaclesEncountered.x * 40} y2={obstaclesEncountered.y * 40} size={M * 40} />
          : <></>} */}
          
          {Array.from({ length: M }).map((_, rowIndex) => <div key={rowIndex}>
            {Array.from({ length: M }).map((_, colIndex) => {
              const isObstacle = obstaclesState.some(ob => ob.x === colIndex && ob.y === rowIndex)
              const isBlue = blueCells.some(bc => bc.x === colIndex && bc.y === rowIndex)
              const isObstacleEncountered = obstaclesEncountered?.x === colIndex && obstaclesEncountered?.y === rowIndex
              const blueClass = isBlue ? 'cellSeeing' : ''
              const obstacleClass = isObstacle ? 'cellObstacle' : ''
              const obstacleEncounteredClass = isObstacleEncountered ? 'cellSelected' : ''
              return <div className={`cell ${blueClass} ${obstacleClass} ${obstacleEncounteredClass} `} key={colIndex} >({colIndex},{rowIndex})</div>
            })}
          </div>)}
        </div>
        
      </form>
    </div>
  )
}
interface AnimatedLineProps {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  size?: number;
}
export function AnimatedLine({ x1, y1, x2, y2, size = 4 }: AnimatedLineProps) {
  return (
    <svg style={{ position: 'absolute', top: '0', left: '0' }} viewBox={`0 0 ${size} ${size}`} xmlns="http://www.w3.org/2000/svg">
      <line
        x1={x1} y1={y1} x2={x2} y2={y2}
        stroke="green" strokeWidth={4}
        pathLength={100}
        style={{
          strokeDasharray: 100,
          strokeDashoffset: 100,
          animation: "draw 0.2s linear forwards"
        }}
      />
      <style>
        {`
          @keyframes draw {
            to { stroke-dashoffset: 0; }
          }
        `}
      </style>
    </svg>
  );
}

export default App
