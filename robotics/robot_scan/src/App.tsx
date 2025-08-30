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


interface SetUpFormI {
  M: number,
  N: number,
  obstacles: {x: number, y: number}[],
}
export function SetUp() {
  const form = useForm<SetUpFormI>({
    defaultValues: { M: 10, N: 10, obstacles: [ { x: 2, y: 1 }, { x: 5, y: 2 } , { x: 6, y: 7 } ] }
  })
  const obstacles = useFieldArray({
    control: form.control,
    name: "obstacles"
  })
  const M = form.watch("M")
  const N = form.watch("N")
  return (
    <div>
      <h1>Set Up Your Environment</h1>
      <form>
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
        
        {/* display the grid */}
        <div style={{ display: 'grid', gridTemplateColumns: `repeat(${M}, 40px)`, gap: '2px', marginTop: '20px' }}>
          {Array.from({ length: M * N }).map((_, index) => {
            const x = index % M
            const y = Math.floor(index / M)
            const isObstacle = obstacles.fields.some(ob => ob.x === x && ob.y === y)
            return (
              <div key={index} style={{ width: '40px', height: '40px', backgroundColor: isObstacle ? 'black' : 'lightgrey', border: '1px solid white', color: 'red' }}>({x},{y})</div>
            )
          })}
        </div>
      </form>
    </div>
  )
}
export default App
