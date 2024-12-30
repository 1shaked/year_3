import { useState } from "react";
import "./App.css";
import {
  useQuery,
  useMutation,
  useQueryClient,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
const queryClient = new QueryClient();

function App() {
  return (
    <div className="App">
      <QueryClientProvider client={queryClient}>
        <div>

          <CommentsChecker />
        </div>
      </QueryClientProvider>

    </div>
  );
}

export function CommentsChecker() {
  const [comments, setComments] = useState<string[]>([
    "This is an amazing movie",
  ]);
  const [reviews , setReviews] = useState<{
    probability: number;
    label: 'negative' | 'positive';
  }[]>([]);
  const [modelType, setModelType] = useState<'GRU-TWO-LAYERS' | 'LSTM-TWO-LAYERS'>('GRU-TWO-LAYERS');
  
  return (
    <div>
      <div style={{ display: "flex", gap: '2rem'}}>
        
        
        <div>
          <label>
            <input
              type="radio"
              value="GRU-TWO-LAYERS"
              checked={modelType === 'GRU-TWO-LAYERS'}
              onChange={() => setModelType('GRU-TWO-LAYERS')}
            />
            GRU-TWO-LAYERS
          </label>
        </div>
        <div>
          <label>
            <input
              type="radio"
              value="LSTM-TWO-LAYERS"
              checked={modelType === 'LSTM-TWO-LAYERS'}
              onChange={() => setModelType('LSTM-TWO-LAYERS')}
            />
            LSTM-TWO-LAYERS
          </label>
        </div>
      </div>
      <div>
        <button
        onClick={() => {
          setComments([...comments, "Movie is amazing"]);
        }}
        >Add comment</button>

      </div>
      {comments.map((comment, i) => (
        <div key={i}>
          <input
            style={{ border: "1px solid green" }}
            type="text"
            value={comment}
            onChange={(e) => {
              const newComments = comments.slice();
              newComments[i] = e.target.value;
              setComments(newComments);
            }}
          />
          <button
            onClick={() => {
              const newComments = comments.slice();
              newComments.splice(i, 1);
              setComments(newComments);
              // 
              setReviews(reviews.filter((_, index) => index !== i));
            }}
          >
            Delete
          </button>
          <div>
            {reviews?.at(i)?.label} {reviews?.at(i)?.probability}
          </div>
        </div>
      ))}
      <div>
        <button
        onClick={async () => {
          const response = await fetch(`https://nlp-comments-analyser.onrender.com/predict/`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ comments, model: modelType }),
          });
          const data = await response.json();
          console.log(data);
          setReviews(data.results);
        }}
        >Send to check</button>
      </div>
    </div>
  );
}

export default App;
