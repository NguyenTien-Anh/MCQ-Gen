import { useState, ChangeEvent, FormEvent } from "react";
import * as pdfjsLib from "pdfjs-dist";
import JSZip from "jszip";
import { Document as DocxDocument } from "docx";

// Set up PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js`;

export const MainContent = () => {
  // const [selectedFileName, setSelectedFileName] =
  //   useState<string>("No file chosen");
  // const [fileContent, setFileContent] = useState<string | null>(null);
  const [inputText, setInputText] = useState<string>("");
  const [topic, setTopic] = useState<string>("");
  const [quantity, setQuantity] = useState<number>(1);
  const [difficulty, setDifficulty] = useState<string>("auto");
  const [mcqResult, setMcqResult] = useState<any[]>([]);
  // const [previewData, setPreviewData] = useState<string | null>(null);
  const [isFileUpload, setIsFileUpload] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);

  // const handleFileInputChange = async (
  //   event: ChangeEvent<HTMLInputElement>
  // ) => {
  //   const file = event.target.files?.[0];
  //   if (file) {
  //     const fileType = file.type;

  //     if (fileType === "application/pdf") {
  //       const reader = new FileReader();
  //       reader.readAsArrayBuffer(file);
  //       reader.onload = async () => {
  //         try {
  //           const typedArray = new Uint8Array(reader.result as ArrayBuffer);
  //           const pdf = await pdfjsLib.getDocument({ data: typedArray })
  //             .promise;
  //           let textContent = "";
  //           for (let i = 1; i <= pdf.numPages; i++) {
  //             const page = await pdf.getPage(i);
  //             const text = await page.getTextContent();
  //             text.items.forEach((item: any) => {
  //               textContent += item.str + " ";
  //             });
  //           }
  //           setFileContent(textContent);
  //         } catch (error) {
  //           console.error("Error reading PDF file:", error);
  //           setFileContent(
  //             "Error reading PDF file. Check console for details."
  //           );
  //         }
  //       };
  //     } else if (fileType === "text/plain") {
  //       const reader = new FileReader();
  //       reader.readAsText(file);
  //       reader.onload = () => {
  //         setFileContent(reader.result as string);
  //       };
  //     } else if (
  //       fileType ===
  //       "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  //     ) {
  //       const reader = new FileReader();
  //       reader.readAsArrayBuffer(file);
  //       reader.onload = async () => {
  //         try {
  //           const zip = new JSZip();
  //           const content = await zip.loadAsync(reader.result as ArrayBuffer);
  //           const doc = await DocxDocument.load(content);
  //           let paragraphs = "";
  //           doc.paragraphs.forEach((paragraph) => {
  //             paragraphs += paragraph.text + "\n";
  //           });
  //           setFileContent(paragraphs);
  //         } catch (error) {
  //           console.error("Error reading DOCX file:", error);
  //           setFileContent(
  //             "Error reading DOCX file. Check console for details."
  //           );
  //         }
  //       };
  //     }

  //     setSelectedFileName(file.name);
  //   } else {
  //     setSelectedFileName("No file chosen");
  //   }
  // };

  const handleFormSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true); // Set loading state to true

    const formData = new FormData();
    formData.append("topic", topic);
    formData.append("quantity", quantity.toString());
    formData.append("difficulty", difficulty);

    if (isFileUpload) {
      const fileInput = document.getElementById(
        "fileInput"
      ) as HTMLInputElement;
      if (fileInput?.files?.[0]) {
        formData.append("file", fileInput.files[0]);
      }
    } else {
      formData.append("inputText", inputText);
    }

    try {
      const response = await fetch("http://127.0.0.1:5000/api/mcq", {
        method: "POST",
        body: formData
      });

      const result = await response.json()

      const mcqs = result.mcqs.map((item: string) => {
        const lines = item.split('\n');
        const question = lines[0];
        const choices = lines.slice(1, lines.length - 1);
        const correctAnswer = lines[lines.length - 1];

        return {
          question,
          choices,
          correctAnswer
        };
      });

      setMcqResult(mcqs);
    } catch (error) {
      setMcqResult([{ error: error.message }]);
    } finally {
      setLoading(false); // Reset loading state
    }
  };

  // const handlePreview = () => {
  //   const preview = `
  //     Topic: ${topic}
  //     Quantity: ${quantity}
  //     Difficulty: ${difficulty}
  //     File: ${selectedFileName}
  //     Input Text: ${isFileUpload ? "N/A" : inputText}
  //   `;
  //   setPreviewData(preview);
  // };

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
                  accept=".pdf"
                  // accept=".pdf,.txt,.docx"
                  // onChange={handleFileInputChange}
                  disabled={loading}
                />
                {/* <p className="text-gray-500 mt-2">{selectedFileName}</p> */}
              </label>
            ) : (
              <label className="block mb-4">
                <span className="text-gray-700">Enter Text:</span>
                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  className="block w-full p-2 border border-gray-300 rounded"
                  rows={4}
                  disabled={loading}
                />
              </label>
            )}
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
                required
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
                <span className="text-gray-700">Difficulty:</span>
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  className="block w-full p-2 border border-gray-300 rounded"
                  disabled={loading}
                >
                  <option value="auto">Auto</option>
                  <option value="dễ">Easy</option>
                  <option value="trung bình">Medium</option>
                  <option value="cao">Hard</option>
                </select>
              </label>
            </div>
            {/* <button
              type="button"
              onClick={handlePreview}
              className="w-full py-2 px-4 bg-gray-500 text-white rounded hover:bg-gray-600 transition duration-200"
            >
              Preview Data
            </button> */}
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

        {/* {previewData && (
          <div className="border border-gray-300 rounded-lg p-4 mt-6">
            <h2 className="text-lg font-medium mb-2">Form Data Preview</h2>
            <pre className="bg-gray-50 p-4 border border-gray-200 rounded overflow-auto">
              {previewData}
            </pre>
          </div>
        )} 

        <div className="border border-gray-300 rounded-lg p-4 mt-6">
          <h2 className="text-lg font-medium mb-2">File Content</h2>
          <pre className="bg-gray-50 p-4 border border-gray-200 rounded overflow-auto">
            {fileContent || "No content available"}
          </pre>
        </div> */}

        {!loading ? (<div className="border border-gray-300 rounded-lg p-4 mt-6">
          <h2 className="text-lg font-medium mb-2">Results</h2>
          {mcqResult.length > 0 ? (
            mcqResult.map((mcq, index) => (
              <div key={index} className="mb-4">
                <p className="font-medium">{index+1}. {mcq.question}</p>
                  {mcq.choices.map((choice, idx) => (
                    <p key={idx} className="ml-4">
                      {choice}
                    </p>
                  ))}
                <p className="text-gray-600">
                  {/* Correct Answer:{" "} */}
                  <span className="font-semibold">{mcq.correctAnswer}</span>
                </p>
              </div>
            ))
          ) : (
            <p className="text-center">No results available</p>
          )}
        </div>
        ) : (
          <p className="text-center">Please wait</p>
        )}
      </div>
      <footer className="mt-8 text-gray-500 text-sm">
        <p className="text-center">
        By Nguyen Tien Anh & Ngo Tien Duc
        </p>
      </footer>
    </div>
  );
};
