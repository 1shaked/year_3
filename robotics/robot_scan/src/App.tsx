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
function toNumber(value: string | number) {
  return typeof value === 'string' ? parseInt(value) : value
}
interface SetUpFormI {
  M: number, // x axis
  N: number, // y axis
  obstacles: {x: number, y: number}[],
}
export function SetUp() {
  const form = useForm<SetUpFormI>({
    defaultValues: { M: 10, N: 10, obstacles: [ { x: 1, y: 4 } , { x: 2, y: 1 }, { x: 5, y: 2 } , { x: 6, y: 7 } ] }
  })
  const obstacles = useFieldArray({
    control: form.control,
    name: "obstacles"
  })
  const M = form.watch("M")
  const N = form.watch("N")


  const [obstaclesState, setObstaclesState] = useState<{x: number, y: number}[]>([])
  const [blueCells, setBlueCells] = useState<{x: number, y: number}[]>([])
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
          console.log('obstaclesState after removal: ', obstaclesState)
          console.log(`Encountered an obstacle at (${cell.x}, ${cell.y}). Stopping the scan in this column. And returning home.`)
          markedCells.push({x: cell.x, y: cell.y})
          i = i - 1
          await sleep(200)
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
      <h1>Set Up Your Environment</h1>
      <form onSubmit={form.handleSubmit((data) => {
        data.obstacles = data.obstacles.map(ob => ({ x: toNumber(ob.x), y: toNumber(ob.y) }))
        console.log(data.obstacles.map(ob => ({ x: toNumber(ob.x), y: toNumber(ob.y) })))
        setObstaclesState(_ => data.obstacles.map(ob => ({ x: toNumber(ob.x), y: toNumber(ob.y) })))
      })}>
        <label>Grid Size</label>
        <input type="number" {...form.register("M")} />
        <input type="number" {...form.register("N")} />
        <br />
        <label>Obstacles</label>
        {obstacles.fields.map((field, index) => (
          <div key={field.id}>
            <input type="number" {...form.register(`obstacles.${index}.x`)} />
            <input type="number" {...form.register(`obstacles.${index}.y`)} />
            <button type="button" onClick={() => obstacles.remove(index)}>Remove</button>
          </div>
        ))}
        <button type="button" onClick={() => obstacles.append({ x: 0, y: 0 })}>Add Obstacle</button>
        <br />
        <br />
        <button type="submit">Run Algorithm</button>
        <button type='button' onClick={() => {
          runAlgorithm()
        }}>test</button>
        {/* display the grid */}
        <div style={{ display: 'grid', gridTemplateColumns: `repeat(${M}, 40px)`, gap: '2px', marginTop: '20px' }}>
          {/* Draw all the rows in the grid */}
          {Array.from({ length: N }).map((_, rowIndex) => <div key={rowIndex}>
            {Array.from({ length: M }).map((_, colIndex) => {
              const isObstacle = obstaclesState.some(ob => ob.x === colIndex && ob.y === rowIndex)
              const isBlue = blueCells.some(bc => bc.x === colIndex && bc.y === rowIndex)
              if (isBlue) {
                return <div key={colIndex} style={{ width: '40px', height: '40px', backgroundColor: 'blue', border: '1px solid white', color: 'red' }}>({ rowIndex} , {colIndex})</div>
              }
              if (isObstacle) {
                return <div key={colIndex} style={{ width: '40px', height: '40px', backgroundColor: 'white', border: '1px solid white', color: 'red' }}>({rowIndex} , {colIndex})</div>
              }
              return <div key={colIndex} style={{ width: '40px', height: '40px', border: '1px solid white', color: 'red' }}>({rowIndex},{colIndex})</div>
            })}
          </div>)}
          {/* <pre>
            {JSON.stringify(blueCells, null, 2)}
          </pre> */}
          <pre>
            {JSON.stringify(obstaclesState  , null, 2)}
          </pre>
          {/* {Array.from({ length: M * N }).map((_, index) => {
            const x = index % M
            const y = Math.floor(index / M)
            const isObstacle = obstaclesState.some(ob => ob.x === x && ob.y === y)
            const isBlue = blueCells.some(bc => bc.x === x && bc.y === y)
            if (isBlue) {
              return (
                <div key={index} style={{ width: '40px', height: '40px', backgroundColor: 'blue', border: '1px solid white', color: 'red' }}>({x},{y})</div>
              )
            }
            return (
              <div key={index} style={{ width: '40px', height: '40px', backgroundColor: isObstacle ? 'black' : 'lightgrey', border: '1px solid white', color: 'red' }}>({x},{y})</div>
            )
          })} */}
        </div>
      </form>
    </div>
  )
}
export default App
