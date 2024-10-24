import { Button } from "./ui/button";

export const Header = () => {
  return (
    <div className=" bg-white/80 py-4 fixed right-0 left-0 ">
      <div className="max-w-screen-xl m-auto flex justify-between items-center px-3">
        <h2 className="font-bold text-lg">📚 MCQ Generator</h2>

        {/* <Button>
          <a href="https://github.com/NguyenTien-Anh/MCQ-Gen">
            Star on Github ❤
          </a>
        </Button> */}
      </div>
    </div>
  );
};
