import '../App.css';
import interview from '../images/interview.PNG'
function Home() {

    const images = [
        {id:1, image:interview},
    ]

    return(
        <>
 <div className="min-h-screen flex flex-col">
      {/* Main Body */}
      <div className="relative flex-grow flex">
        {/* Text Section */}
        <div className="w-2/3 bg-blue-500 text-white flex flex-col justify-center items-center p-8 relative">
          <h1 className="text-4xl font-bold mb-4">Welcome to MockSmart</h1>
          <p className="text-lg">
            Elevate your interview skills with AI-powered insights. 
            MockSmart
            analyzes your responses, expressions, and body language to help you
            shine in your next interview.
          </p>

          {/* Call to Action Button */}
          <button
            // onClick={toggleModal}
            className="px-6 py-3 bg-orange-500 text-white rounded-lg text-lg font-semibold hover:bg-orange-600 transition duration-300 mt-24"
          >
            Get Started
          </button>
        

          
        </div>

        {/* Image Section */}
        <div
          className="w-1/3 bg-cover bg-center"
          style={{
            backgroundImage: "url('/path-to-your-image.jpg')",
          }}
        >
            <img
                    src={images[0].image}
                    alt="Cover photo"
                    className="w-full h-full object-cover"
                />
        </div>
      </div>

      
    </div>
        </>
    )
}
export default Home;