import {
  useQuery,
  useMutation,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import { useState } from "react";

// Create a Query Client
const queryClient = new QueryClient();

export const MAPPING_VALUES_ARRAY = [
  "T-shirt/top",
  "Trouser",
  "Pullover",
  "Dress",
  "Coat",
  "Sandal",
  "Shirt",
  "Sneaker",
  "Bag",
  "ANkle boot",
];

const url = "http://127.0.0.1:8000";

interface FashionData {
  data: number[][];
  predictions: number[];
}

interface ImageProps {
  pixels: number[];
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "1rem" }}>
        <FashionList />
      </div>
    </QueryClientProvider>
  );
}

// Component 1: FashionList
function FashionList() {
  const [imagesNumber, setImagesNumber] = useState(10);
  const [model, setModel] = useState("LAST_TRAIN_MODEL.json");

  const get_models = useQuery({
    queryKey: ["get_models"],
    queryFn: async () => {
      const response = await fetch(`${url}/get_models/`);
      const data = (await response.json()) as string[];
      return data;
    },
  });

  const [predictions, setPredictions] = useState<FashionData>({
    data: [],
    predictions: [],
  });

  const images_mutation = useMutation({
    mutationFn: async () => {
      const response = await fetch(`${url}/get_examples/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: model,
          number_of_samples: imagesNumber,
        }),
      });
      const data = (await response.json()) as FashionData;
      return data;
    },
    onSuccess: (data) => {
      setPredictions(data);
    },
  });
  const [search, setSearch] = useState("");

  return (
    <div>
      <h1 style={{ fontSize: "2rem", color: "rgba(255, 255, 255, 0.87)" }}>
        Fashion MNIST Model Viewer
      </h1>

      

      <div>
        <h2 style={{ color: "rgba(255, 255, 255, 0.87)", marginBottom: "1rem" , display: "flex", gap: "2rem",
          alignItems: "center"
        }}>
          <div style={{ fontSize: "4rem"}}>Models</div>
          <input 
          style={{ fontSize: "2rem" }}
          type="text" placeholder="search model" value={search}
          onChange={(e) => {
            setSearch(e.target.value);
          }} />

          <div>
          <div style={{ marginBottom: "1.5rem" }}>
        <label style={{ display: "block", marginBottom: "0.5rem" }}>
          Number of Images:
        </label>
        <input
      
          type="number"
          onChange={(e) => setImagesNumber(parseInt(e.target.value))}
          value={imagesNumber}
          style={{
            padding: "0.5rem",
            fontSize: "2rem",
            border: "1px solid #ccc",
            borderRadius: "5px",
            width: "100px",

          }}
        />
      </div>
          </div>
        </h2>
        <div
          style={{
            display: "flex",
            gap: "1rem",
            overflowX: "auto",
          }}
        >
          {get_models.data?.filter((v) => { return v.includes(search) }).map((model, index) => (
            <div
              key={index}
              onClick={() => setModel(model)}
              style={{
                border: model === model ? "2px solid #646cff" : "1px solid #ccc",
                padding: "1rem",
                cursor: "pointer",
                borderRadius: "8px",
                backgroundColor: "#1a1a1a",
                transition: "transform 0.2s, box-shadow 0.2s",
              }}
            >
              <DisplayModel model={model} />
            </div>
          ))}
        </div>
      </div>

      <button
        type="button"
        onClick={() => images_mutation.mutate()}
        style={{
          backgroundColor: "#646cff",
          color: "#fff",
          border: "none",
          padding: "10px 20px",
          fontSize: "16px",
          borderRadius: "5px",
          cursor: "pointer",
          marginTop: "1rem",
        }}
      >
        Fetch Images
      </button>

      <hr style={{ margin: "2rem 0", borderColor: "#ccc" }} />

      <h2 style={{ color: "rgba(255, 255, 255, 0.87)" }}>Images</h2>
      <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
        gap: "20px",
      }}>
        {predictions.data.map((image, index) => (
          <div
            key={index}
            style={{
              marginBottom: "20px",
              padding: "10px",
              border: "1px solid #ccc",
              borderRadius: "5px",
              backgroundColor: "#1a1a1a",
            }}
          >
            <h3
              style={{
                marginBottom: "10px",
                color: "white",
                fontSize: "1.5rem",
                textAlign: "center",
              }}
            >
              {MAPPING_VALUES_ARRAY.at(predictions.predictions[index]) ?? "Error"}
            </h3>
            <div
              
            >
              <Image pixels={image} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Component 2: DisplayModel
export function DisplayModel({ model }: { model: string }) {
  const parts = model.replace(".json", "").split("_");

  const batchSize = parts[1];
  const learningRate = parts[2];
  const hiddenSize = parts[3];
  const epochs = parts[4];

  return (
    <div>
      <h3>{model.replace(".json", "")}</h3>
      <p>Batch size: {batchSize}</p>
      <p>Learning rate: {learningRate}</p>
      <p>Hidden size: {hiddenSize}</p>
      <p>Epochs: {epochs}</p>
    </div>
  );
}

// Component 3: Image
function Image({ pixels }: ImageProps) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(28, 10px)",
        gridGap: "1px",
      }}
    >
      {pixels.map((pixel, index) => (
        <div
          key={index}
          style={{
            width: "10px",
            height: "10px",
            backgroundColor: `rgb(${pixel}, ${pixel}, ${pixel})`,
          }}
        ></div>
      ))}
    </div>
  );
}
