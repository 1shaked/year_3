import {
  useQuery,
  useMutation,
  useQueryClient,
  QueryClient,
  QueryClientProvider,
} from '@tanstack/react-query'
import { useState } from 'react'

// Create a client
const queryClient = new QueryClient()

function App() {
  return (
    // Provide the client to your App
    <QueryClientProvider client={queryClient}>
      <FashionList />
    </QueryClientProvider>
  )
}

export const MAPPING_VALUES = {
  0: 'T-shirt/top',
  1: 'Trouser',
  2: 'Pullover',
  3: 'Dress',
  4: 'Coat',
  5: 'Sandal',
  6: 'Shirt',
  7: 'Sneaker',
  8: 'Bag',
  9: 'Ankle boot',
} 
export const MAPPING_VALUES_ARRAY =[
  'T-shirt/top',
  'Trouser',
  'Pullover',
  'Dress',
  'Coat',
  'Sandal',
  'Shirt',
  'Sneaker',
  'Bag',
  'Ankle boot',
]
const url = 'http://127.0.0.1:8000'
interface FashionData {
  'data': number[][],
  'predictions': number[]
}
function FashionList() {
  const [imagesNumber, setImagesNumber] = useState(2)
  const [model, setModel] = useState('LAST_TRAIN_MODEL.json')
  const get_models = useQuery({
    queryKey: ['get_models'],
    
    queryFn: async () => {
      const response = await fetch(`${url}/get_models/`)
      const data = (await response.json()) as string[]
      return data
    },
  })
  const [predations, setPredictions] = useState<FashionData>({
    data: [],
    predictions: []
  })
  const images_mutation = useMutation({
    mutationFn: async () => {
      const response = await fetch(`${url}/get_examples/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: model,
          number_of_samples: imagesNumber
        }),
      })
      const data = (await response.json()) as FashionData
      return data
    },
    onSuccess: (data) => {
      setPredictions(data)
    },
  })
  return (
    <div>
      <h2>Number of images you want</h2>
      <input type="number" onChange={(e) => {
        setImagesNumber(parseInt(e.target.value))
      }} 
      value={imagesNumber} />
      <h2>Models</h2>
      <div style={{ display: 'flex', gap: '2rem' }}>
        {get_models.data?.map((model, index) => (
          <div key={index} onClick={() => {
            setModel(model)
          }}><DisplayModel model={model} /></div>
        ))}
      </div>
      <button type="button" onClick={() => images_mutation.mutate()}>
        Fetch images
      </button>
      <hr />
      <h2>Images</h2>
      {predations.data.map((image, index) => (
        <div key={index}>
          {MAPPING_VALUES_ARRAY.at(predations.predictions[index]) ?? 'Error'}
          predations - {JSON.stringify(predations.predictions[index])}
          <br />
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
            <Image pixels={image} />
          </div>
          
        </div>
      ))}
    </div>
  )
}

export function DisplayModel({ model }: { model: string }) {
  const parts = model.replace(".json", "").split("_"); // Remove .json and split by "_"

  // Extract each parameter
  const batchSize = parts[1];
  const learningRate = parts[2];
  const hiddenSize = parts[3];
  const epochs = parts[4];
  return <div style={{ border: "1px solid black", padding: "1rem", cursor: "pointer" }}>
    <h2>{model.replace('.json', '')}</h2>
    <p>Batch size: {batchSize}</p>
    <p>Learning rate: {learningRate}</p>
    <p>Hidden size: {hiddenSize}</p>
    <p>Epochs: {epochs}</p>

  </div>
}

interface ImageProps {
  pixels: number[]
}
function Image({ pixels }: ImageProps) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(28, 10px)", // Each image is 28x28 grid
        gridGap: "1px",
      }}
    >
      {pixels.map((pixel, index) => (
        <div
          key={index}
          style={{
            width: "10px",
            height: "10px",
            backgroundColor: `rgb(${pixel}, ${pixel}, ${pixel})`, // 1 = black, 0 = white
          }}
        ></div>
      ))}
    </div>
  );
}

export default App
