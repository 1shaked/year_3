import { useState } from "react";
import "./App.css";
import {
  useQuery,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";

// Create a client
const queryClient = new QueryClient();

function App() {
  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <QueryClientProvider client={queryClient}>
        <ReportPage />
      </QueryClientProvider>
    </div>
  );
}

export default App;

import { Puff } from "react-loader-spinner";
import { API_BASE_URL } from "./const";

export function ReportPage() {
  const get_models = useQuery({
    queryKey: ["get_models"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE_URL}/get_models`)
      const data = (await res.json()) as { file: string, name: string, lr: number, weight_decay: string}[] 
      return {
        models: data,
      };
    },
  });

  const [selectedModel, setSelectedModel] = useState<string[]>([]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-center text-gray-800">Report- STL-10 (<a target="_blank" className=" text-blue-500" href="https://github.com/1shaked/year_3/tree/main/DL/ex3">github</a>)</h1>
      <div>
        {get_models.isLoading ? (
          <div className="flex justify-center items-center">
            <Puff
              visible={true}
              height="80"
              width="80"
              color="#4fa94d"
              ariaLabel="puff-loading"
            />
          </div>
        ) : (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            {get_models?.data?.models.map((model) => (
              <div key={model.name}>
                <div
                  className={`p-6 border rounded-lg shadow-md hover:shadow-xl transition-all cursor-pointer ${
                    selectedModel?.includes(model.file)
                      ? "bg-emerald-100 border-emerald-600"
                      : "bg-white"
                  }`}
                  onClick={() =>
                    setSelectedModel(
                      selectedModel?.includes(model.file)
                        ? selectedModel.filter((m) => m !== model.file)
                        : [...(selectedModel || []), model.file]
                    )
                  }
                >
                  <h2 className="text-lg font-bold text-gray-800">
                    {model.name}
                  </h2>
                  <div className="flex justify-between items-center">
                    <p className="text-sm text-gray-600">
                      <span className="font-semibold">Learning Rate:</span>{" "}
                      {model.lr}
                    </p>
                    <p className="text-sm text-gray-600">
                      <span className="font-semibold">Weight Decay:</span>{" "}
                      {model.weight_decay}
                    </p>
                  </div>
                </div>
                <div className="pt-2">
                  {selectedModel.includes(model.file) ? (
                    <>
                      <div className="p-6 border rounded-lg shadow-md bg-white">
                        <DisplayModel
                          key={model.file}
                          model={{
                            name: model.name,
                            lr: model.lr,
                            weight_decay: model.weight_decay,
                            file: model.file,
                          }}
                        />
                      </div>
                    </>
                  ) : (
                    <></>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

interface DisplayModelProps {
  model: {
    name: string;
    lr: number;
    weight_decay: string;
    file: string;
  };
}

import Plot from "react-plotly.js";

export function DisplayModel(props: DisplayModelProps) {
  const get_model_data = useQuery({
    queryKey: ["get_model_data", props.model.name],
    queryFn: async () => {
      const res = await fetch(`${API_BASE_URL}/get_model/${props.model.file}`)
      const data = (await res.json()) as { acc: number, train_losses: number[], val_losses: number[], train_accuracies: number[], val_accuracies: number[], epochs: number, loss: number, lr: number, wd: number}
      return data;
    },
  });

  return (
    <div className="space-y-4">
      {get_model_data.isLoading || get_model_data.data === undefined ? (
        <div className="flex justify-center items-center">
          <Puff
            visible={true}
            height="80"
            width="80"
            color="#4fa94d"
            ariaLabel="loading"
          />
        </div>
      ) : (
        <>
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-bold text-gray-800">
            {props.model.name}
          </h3>
          <div>
            <p className="text-sm text-gray-600">
              <span className="font-semibold">Loss:</span>{" "}
              {Number(get_model_data.data.loss).toFixed(4)}
            </p>
            <p className="text-sm text-gray-600">
              <span className="font-semibold">Accuracy:</span>{" "}
              {get_model_data.data.acc * 100}%
            </p>
          </div>
        </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <Plot
              data={[
                {
                  x: Array.from(
                    { length: get_model_data.data.epochs },
                    (_, i) => i + 1
                  ),
                  y: get_model_data.data.train_losses,
                  type: "scatter",
                  mode: "lines+markers",
                  marker: { color: "red" },
                  name: "Train",
                },
                {
                  type: "bar",
                  x: Array.from(
                    { length: get_model_data.data.epochs },
                    (_, i) => i + 1
                  ),
                  y: get_model_data.data.val_losses,
                  marker: { color: "blue" },
                  name: "Val",
                },
              ]}
              layout={{
                width: 350,
                height: 400,
                title: { text: "Losses" },
                legend: {
                  x: 1,
                  y: 0,
                  orientation: "v",
                },
              }}
            />
            {/* acc graph */}
            <Plot
              data={[
                {
                  x: Array.from(
                    { length: get_model_data.data.epochs },
                    (_, i) => i + 1
                  ),
                  y: get_model_data.data.train_accuracies,
                  type: "scatter",
                  mode: "lines+markers",
                  marker: { color: "red" },
                  name: "Train",
                },
                {
                  type: "bar",
                  x: Array.from(
                    { length: get_model_data.data.epochs },
                    (_, i) => i + 1
                  ),
                  y: get_model_data.data.val_accuracies,
                  marker: { color: "blue" },
                  name: "Val",
                },
              ]}
              layout={{
                width: 350,
                height: 400,
                title: { text: "Accuracies" },
                legend: {
                  x: 1,
                  y: 0,
                  orientation: "v",
                },
              }}
            />
          </div>
        </>
      )}
    </div>
  );
}
