interface Props {
  imageUrl: string | null;
  isLoading: boolean;
  error: string | null;
}

export default function ChartPreview({ imageUrl, isLoading, error }: Props) {
  return (
    <div className="flex-1 bg-white border border-gray-200 rounded-lg p-6 flex items-center justify-center">
      {isLoading && (
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
          <p className="text-gray-600">正在渲染图表...</p>
        </div>
      )}

      {error && (
        <div className="text-center text-red-600">
          <p className="text-xl mb-2">⚠️</p>
          <p>{error}</p>
        </div>
      )}

      {imageUrl && !isLoading && !error && (
        <img 
          src={imageUrl} 
          alt="Chart Preview" 
          className="max-w-full h-auto shadow-lg"
        />
      )}

      {!imageUrl && !isLoading && !error && (
        <div className="text-center text-gray-400">
          <p className="text-xl mb-2">📊</p>
          <p>输入数据后点击"渲染图表"</p>
        </div>
      )}
    </div>
  );
}
