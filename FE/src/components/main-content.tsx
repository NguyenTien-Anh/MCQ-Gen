// @ts-nocheck
import { useState, useRef, useEffect, ChangeEvent, FormEvent } from "react";

export const MainContent = () => {
  const [selectedFileName, setSelectedFileName] = useState<string>("No file chosen");
  const [inputText, setInputText] = useState<string>("");
  const [prevInputText, setPrevInputText] = useState<string>("");
  const [topic, setTopic] = useState<string>("");
  const [quantity, setQuantity] = useState<number>(1);
  const [numAnswer, setNumAnswer] = useState<number>(4);
  const [difficulty, setDifficulty] = useState<string>("auto");
  const [notice, setNotice] = useState<string>("");
  const [mcqResult, setMcqResult] = useState<any[]>([]);
  const [isFileUpload, setIsFileUpload] = useState<boolean>(true);
  const [isRecheck, setIsRecheck] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);
  const [status, setStatus] = useState<boolean>(false);
  const [questionType, setQuestionType] = useState<string>("SingleChoice");
  const be_url = import.meta.env.VITE_BE_URL

  const resultRef = useRef<HTMLDivElement>(null);

  const handleQuestionTypeChange = (type: string) => {
    setQuestionType(type);
  };

  useEffect(() => {
    if (mcqResult.length > 0 && resultRef.current) {
      resultRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [mcqResult]);

  const handleFileInputChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const fileInput = event.target as HTMLInputElement;
    if (fileInput.files && fileInput.files.length > 0) {
      setStatus(true); // Set status to true if a file is selected
      setSelectedFileName(fileInput.files[0].name); // Update the file name display
    } else {
      setStatus(false); // Set status to false if no file is selected
      setSelectedFileName("No file chosen"); // Reset the file name display
    }
  };

  const handleFormSubmit = async (event: FormEvent) => {


    event.preventDefault();
    setLoading(true);

    const formData = new FormData();
    formData.append("topic", topic);
    formData.append("quantity", quantity.toString());
    formData.append("difficulty", difficulty);
    formData.append("status", status.toString());
    formData.append("questionType", questionType);
    formData.append("numAnswer", numAnswer.toString());
    formData.append("isRecheck", isRecheck.toString());

    if (isFileUpload) {
      const fileInput = document.getElementById("fileInput") as HTMLInputElement;
      if (fileInput?.files?.[0]) {
        formData.append("file", fileInput.files[0]);
      }
    } else {
      formData.append("inputText", inputText);
    }
    // console.log("url: ", be_url)

    try {
      const response = await fetch(`${be_url}/api/mcq`, {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const result = await response.json();
      // console.log(typeof result.mcqs)
      const mcqs = result.mcqs.map(item => {
        const correctAnswers = item.answers
          .filter(answer => answer.isCorrectAnswer === "true")
          .map(answer => answer.answer);

        return {
          "question": item.question.replace(/\"/g, ""), // Loại bỏ dấu ngoặc kép thừa
          "choices": item.answers.map(answer => answer.answer),
          "correctAnswer": correctAnswers.join(" - ") // Kết hợp các đáp án đúng thành một chuỗi
        };
      });
      // console.log("mcqs: ", mcqs)
      setNotice(result.notify)
      setMcqResult(mcqs);
      setStatus(false);

    } catch (error) {
      setMcqResult([{ error: (error as Error).message }]);
    } finally {
      setLoading(false);
    }
  };

  const handleInputTextChange = (event: ChangeEvent<HTMLTextAreaElement>) => {
    const newInputText = event.target.value;
    setInputText(newInputText);

    if (newInputText !== prevInputText) {
      setStatus(true);
    } else {
      setStatus(false);
    }

    setPrevInputText(newInputText);
  };

  return (
    <div className="bg-gray-100 min-h-screen flex flex-col items-center py-10">
      <div className="container mx-auto max-w-3xl p-6 bg-white shadow-md rounded-lg">
        <form onSubmit={handleFormSubmit} className="space-y-6">
          <div className="text-center">
            <h1 className="text-2xl font-semibold mb-4">
              Upload File or Enter Text to Generate MCQs
            </h1>
          </div>

          <div className="border border-gray-300 rounded-lg p-4">
            <h2 className="text-lg font-medium mb-2">Input Method</h2>
            <div className="flex items-center mb-4">
              <input
                type="radio"
                id="fileUpload"
                checked={isFileUpload}
                onChange={() => setIsFileUpload(true)}
                className="mr-2"
              />
              <label htmlFor="fileUpload" className="text-gray-700">
                Upload File
              </label>
              <input
                type="radio"
                id="textInput"
                checked={!isFileUpload}
                onChange={() => setIsFileUpload(false)}
                className="ml-4 mr-2"
              />
              <label htmlFor="textInput" className="text-gray-700">
                Enter Text
              </label>
            </div>

            {isFileUpload ? (
              <label className="block mb-4">
                <span className="text-gray-700">Choose File:</span>
                <input
                  type="file"
                  id="fileInput"
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:border file:border-gray-300 file:rounded file:text-sm file:font-medium file:bg-gray-50 file:text-gray-700 hover:file:bg-gray-100"
                  accept=".pdf, .doc, .docx, .txt"
                  onChange={handleFileInputChange}
                  disabled={loading}
                />
                <p className="text-gray-500 mt-2">{selectedFileName}</p>
              </label>
            ) : (
              <label className="block mb-4">
                <span className="text-gray-700">Enter Text:</span>
                <textarea
                  value={inputText}
                  onChange={handleInputTextChange}
                  className="block w-full p-2 border border-gray-300 rounded"
                  rows={4}
                  disabled={loading}
                />
              </label>
            )}
          </div>

          <div className="border border-gray-300 rounded-lg p-4">
            <h2 className="text-lg font-medium mb-2">Question type</h2>
            <div className="flex items-center mb-4">
              <input
                type="radio"
                id="SingleChoice"
                checked={questionType === "SingleChoice"}
                onChange={() => { handleQuestionTypeChange("SingleChoice"), setNumAnswer(4) }}
                className="ml-4 mr-2"
              />
              <label htmlFor="SingleChoice" className="text-gray-700">
                Single choice
              </label>
              <input
                type="radio"
                id="MultipleChoice"
                checked={questionType === "MultipleChoice"}
                onChange={() => { handleQuestionTypeChange("MultipleChoice"), setNumAnswer(4) }}
                className="ml-4 mr-2"
              />
              <label htmlFor="MultipleChoice" className="text-gray-700">
                Multiple choice
              </label>
              <input
                type="radio"
                id="TrueFalse"
                checked={questionType === "TrueFalse"}
                onChange={() => { handleQuestionTypeChange("TrueFalse"), setNumAnswer(2) }}
                className="ml-4 mr-2"
              />
              <label htmlFor="TrueFalse" className="text-gray-700">
                True/False
              </label>
            </div>
            <b>Note: Question type - number of answer constraints</b>
            <p>True/False: 2</p>
            <p>Single choice: 2 - 5</p>
            <p>Multiple choice: 3 - 5</p>
            <br></br>
            <h2 className="text-lg font-medium mb-2">Recheck?</h2>
            <div className="flex items-center mb-4">
              <input
                type="radio"
                id="true"
                checked={isRecheck}
                onChange={() => setIsRecheck(true)}
                className="ml-4 mr-2"
              />
              <label htmlFor="true" className="text-gray-700">
                Yes
              </label>
              <input
                type="radio"
                id="false"
                checked={!isRecheck}
                onChange={() => setIsRecheck(false)}
                className="ml-4 mr-2"
              />
              <label htmlFor="false" className="text-gray-700">
                No
              </label>
            </div>
          </div>

          <div className="border border-gray-300 rounded-lg p-4 mt-4">
            <h2 className="text-lg font-medium mb-2">MCQ Parameters</h2>
            <label className="block mb-4">
              <span className="text-gray-700">Topic:</span>
              <input
                type="text"
                id="topic"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="block w-full p-2 border border-gray-300 rounded"
                disabled={loading}
              />
            </label>
            <div className="flex space-x-4">
              <label className="block flex-1">
                <span className="text-gray-700">Quantity:</span>
                <input
                  type="number"
                  id="quantity"
                  min={1}
                  value={quantity}
                  onChange={(e) => setQuantity(Number(e.target.value))}
                  className="block w-full p-2 border border-gray-300 rounded"
                  required
                  disabled={loading}
                />
              </label>
              <label className="block flex-1">
                <span className="text-gray-700">Num of answer:</span>
                <input
                  type="number"
                  id="numAnswer"
                  min={2}
                  max={5}
                  value={numAnswer}
                  onChange={(e) => setNumAnswer(Number(e.target.value))}
                  className="block w-full p-2 border border-gray-300 rounded"
                  required
                  disabled={loading}
                />
              </label>
              <label className="block flex-1">
                <span className="text-gray-700">Difficulty:</span>
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  className="block w-full p-2 border border-gray-300 rounded"
                  disabled={loading}
                >
                  <option value="auto">Auto</option>
                  <option value="nhớ">Remember</option>
                  <option value="hiểu">Understand</option>
                  <option value="áp dụng">Apply</option>
                </select>
              </label>
            </div>
            <button
              type="submit"
              className="w-full py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600 transition duration-200 mt-2"
              disabled={loading}
            >
              {loading ? "Generating..." : "Submit"}
            </button>
          </div>
        </form>

        {loading && (
          <div className="flex justify-center mt-4">
            <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
          </div>
        )}

        {!loading && (
          <div ref={resultRef} className="border border-gray-300 rounded-lg p-4 mt-6">
            <h2 className="text-lg font-medium mb-2">Results</h2>
            <p className="text-gray-600">
              <span className="font-medium">{notice}</span>
            </p>
            {mcqResult.length > 0 ? (
              mcqResult.map((mcq, index) => (
                <div key={index} className="mb-4">
                  <p className="font-medium">{index + 1}. {mcq.question}</p>
                  {mcq.choices.map((choice, idx) => (
                    <p key={idx} className="ml-4">
                      {choice}
                    </p>
                  ))}
                  <p className="text-gray-600">
                    <span className="font-medium">Đáp án đúng:</span> {mcq.correctAnswer}
                  </p>
                </div>
              ))
            ) : (
              <p>No results available</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};