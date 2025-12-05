import { useEffect, useRef, useState } from 'react'
import { Button } from './components/ui/button'
import { Input } from './components/ui/input'
import { Label } from './components/ui/label'
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './components/ui/table'
import { Alert, AlertDescription } from './components/ui/alert'
import { AlertCircle, ChevronLeft, ChevronRight } from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_BASE_URL

interface Person {
  name: string
  imageUrl: string
}

interface PredictionResult {
  num_to_person: Record<string, string>
  result: Array<{
    class: string
    class_probability: number[]
  }>
}

interface ApiError {
  error?: string
  message?: string
}

function App() {
  const sportsMan: Person[] = [
    { name: 'Babar Azam', imageUrl: '/images/babar-azam.jpg' },
    { name: 'Cristiano Ronaldo', imageUrl: '/images/cristiano-ronaldo.jpg' },
    { name: 'Lionel Messi', imageUrl: '/images/lionel-messi.jpg' },
    { name: 'Mohammad Amir', imageUrl: '/images/mohammad-amir.jpg' },
    { name: 'Shaheen Afridi', imageUrl: '/images/shaheen-afridi.jpg' },
    { name: 'Shahid Afridi', imageUrl: '/images/shahid-afridi.jpg' },
    { name: 'Virat Kohli', imageUrl: '/images/virat-kohli.jpg' },
  ]

  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const [prediction, setPrediction] = useState<PredictionResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [currentResultIndex, setCurrentResultIndex] = useState<number>(0)
  const errorRef = useRef<HTMLDivElement>(null)

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0]
      setSelectedImage(file)
      
      // Create preview URL
      const reader = new FileReader()
      reader.onload = (event) => {
        setImagePreview(event.target?.result as string)
      }
      reader.readAsDataURL(file)
      
      // Clear previous prediction and error when new image is selected
      setPrediction(null)
      setError(null)
      setCurrentResultIndex(0)
    } else {
      setSelectedImage(null)
      setImagePreview(null)
      setPrediction(null)
      setError(null)
      setCurrentResultIndex(0)
    }
  }

  const handlePredict = async () => {
    if (!selectedImage) {
      setError('Please select an image first.')
      return
    }

    setLoading(true)
    setPrediction(null)
    setError(null)
    setCurrentResultIndex(0)

    try {
      const toBase64 = (file: File): Promise<string> =>
        new Promise((resolve, reject) => {
          const reader = new FileReader()
          reader.readAsDataURL(file)
          reader.onload = () => resolve(reader.result as string)
          reader.onerror = (error) => reject(error)
        })

      const response = await fetch(`${API_BASE}/classify_image`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image: await toBase64(selectedImage),
        }),
      })

      // Check if response is not OK
      if (!response.ok) {
        const errorData: ApiError = await response.json()
        throw new Error(errorData.error || errorData.message || 'Prediction failed')
      }

      const data: PredictionResult = await response.json()
      console.log('Prediction response:', data)
      setPrediction(data)
    } catch (error: unknown) {
      console.error('Error making prediction:', error)
      
      // Set error message based on the error type
      if (error instanceof Error) {
        if (error.message === "No face with 2 eyes detected.") {
          setError('No face with 2 eyes detected. Please try another image.')
        } else {
          setError('An error occurred while making the prediction. Please try again.')
        }
      } else {
        setError('An unexpected error occurred. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  // Format person name from the prediction class
  const formatPersonName = (className: string): string => {
    return className.replace('_', ' ')
  }

  // Navigate to next result
  const goToNextResult = () => {
    if (prediction && currentResultIndex < prediction.result.length - 1) {
      setCurrentResultIndex(prev => prev + 1)
    }
  }

  // Navigate to previous result
  const goToPrevResult = () => {
    if (currentResultIndex > 0) {
      setCurrentResultIndex(prev => prev - 1)
    }
  }

  // Scroll to error when it appears
  useEffect(() => {
    if (error && errorRef.current) {
      // Scroll to the error element
      errorRef.current.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
      })
    }
  }, [error])

  // Get current result
  const currentResult = prediction?.result?.[currentResultIndex]
  const totalResults = prediction?.result?.length || 0

  return (
    <div className="h-dvh overflow-y-scroll w-full bg-background p-4 flex flex-col items-center">
      <div className="flex flex-wrap justify-center gap-3 mb-8 mt-8">
        {sportsMan.map((person) => (
          <div
            key={person.name}
            className="flex flex-col items-center w-17 md:w-24 lg:w-32"
          >
            <img
              src={person.imageUrl}
              alt={person.name}
              className="rounded-full w-full aspect-square object-cover mb-2 border-2 border-primary"
            />
            <span className="text-sm font-medium text-center">
              {person.name}
            </span>
          </div>
        ))}
      </div>

      <div className="flex flex-col md:flex-row md:gap-8 items-top justify-center w-full">
        <div className="w-full max-w-xs space-y-4 mb-8">
          <div>
            <Label htmlFor="image">Select Image</Label>
            <Input
              id="image"
              type="file"
              className="text-muted-foreground file:border-input file:text-foreground p-0 pr-3 italic file:mr-3 file:h-full file:border-0 file:border-r file:border-solid file:bg-transparent file:px-3 file:text-sm file:font-medium file:not-italic"
              accept="image/*"
              onChange={handleImageChange}
            />
          </div>

          {/* Selected Image Preview */}
          {imagePreview && (
            <div className="space-y-2">
              <Label>Selected Image Preview</Label>
              <div className="border rounded-lg overflow-hidden">
                <img
                  src={imagePreview}
                  alt="Selected preview"
                  className="w-full h-48 object-cover"
                />
              </div>
            </div>
          )}

          <Button onClick={handlePredict} disabled={loading} className="w-full">
            {loading ? 'Classifying...' : 'Classify Image'}
          </Button>

          {/* Error Display */}
          {error && (
            <div ref={errorRef}>
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            </div>
          )}
        </div>

        {/* Prediction Result Section */}
        {prediction && currentResult && (
          <div className="w-full max-w-2xl space-y-6">
            {/* Predicted Person with Pagination */}
            <div className="text-center p-6 bg-card rounded-lg border shadow-sm">
              <div className="flex items-center justify-between mb-4">
                {/* Previous Button */}
                <Button
                  onClick={goToPrevResult}
                  disabled={currentResultIndex === 0}
                  variant="outline"
                  size="icon"
                  className="h-8 w-8"
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>

                {/* Result Title */}
                <div className="flex-1 px-4">
                  <h2 className="text-2xl font-bold mb-2">Prediction Result</h2>
                  {totalResults > 1 && (
                    <div className="text-sm text-muted-foreground mb-2">
                      Face {currentResultIndex + 1} of {totalResults}
                    </div>
                  )}
                </div>

                {/* Next Button */}
                <Button
                  onClick={goToNextResult}
                  disabled={currentResultIndex === totalResults - 1}
                  variant="outline"
                  size="icon"
                  className="h-8 w-8"
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
              
              <p className="text-lg">
                The image is predicted to be:{' '}
                <span className="font-bold text-primary">
                  {formatPersonName(currentResult.class)}
                </span>
              </p>

              {/* Dots Indicator for multiple results */}
              {totalResults > 1 && (
                <div className="flex justify-center items-center gap-2 mt-4">
                  {Array.from({ length: totalResults }).map((_, index) => (
                    <button
                      key={index}
                      onClick={() => setCurrentResultIndex(index)}
                      className={`h-2 w-2 rounded-full transition-all ${
                        index === currentResultIndex
                          ? 'bg-primary w-4'
                          : 'bg-muted-foreground/30 hover:bg-muted-foreground/50'
                      }`}
                      aria-label={`Go to result ${index + 1}`}
                    />
                  ))}
                </div>
              )}
            </div>

            {/* Probability Table */}
            <div className="border rounded-lg shadow-sm overflow-hidden">
              <div className="p-4 bg-muted border-b">
                <p className="text-sm text-muted-foreground">
                  This table shows the probability scores for each person. The model predicts which sports person is most likely to be in the image based on these scores.
                </p>
              </div>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-1/2">Person</TableHead>
                    <TableHead className="w-1/2 text-right">Probability Score</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {currentResult.class_probability.map((score, index) => {
                    const personKey = index.toString()
                    const personName = prediction.num_to_person[personKey]
                    const formattedName = formatPersonName(personName)
                    
                    return (
                      <TableRow key={index}>
                        <TableCell className="font-medium">{formattedName}</TableCell>
                        <TableCell className="text-right">
                          {score.toFixed(2)}%
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
                <TableCaption className="p-4 border-t">
                  Note: Higher probability scores indicate stronger confidence in the prediction.
                </TableCaption>
              </Table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App