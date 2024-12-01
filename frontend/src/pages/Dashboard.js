import { useState, useEffect } from "react";



const Dashboard = () => {

    

    // Retrieve user details from localStorage
    const storedUserDetails = localStorage.getItem('user_details');
    const userDetails = storedUserDetails ? JSON.parse(storedUserDetails) : null;
    const [activeSection, setActiveSection] = useState('Dashboard');
    const [videoTitle, setVideoTitle] = useState('');
    const [videoFile, setVideoFile] = useState(null);
    const [isAnalyzeEnabled, setIsAnalyzeEnabled] = useState(false);
    const [uploadStatus, setUploadStatus] = useState('');
    const [analysisStatus, setAnalysisStatus] = useState('');
    const [videoId, setVideoId] = useState(null)
    const [analysisResults, setAnalysisResults] = useState({feedback: [],
      confidence_score: null,
      clarity_score: null,
      body_language_score: null,
      avd_sentence_length: null,
      filler_word_count: null,
      eye_contact: null,});
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [videos, setVideos] = useState([]);
    const [isResultsModalOpen, setIsResultsModalOpen] = useState(false)
    const [feedback, setFeedback] = useState([]);
    const [selectedFeedback, setSelectedFeedback] = useState(null);

    // Fetch videos based on user_id
  useEffect(() => {
    const fetchVideos = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/videos/`);
        const data = await response.json();
        // Filter videos for the logged-in user
        const userVideos = data.filter((video) => video.user_id === userDetails.id);
        setVideos(userVideos);
      } catch (error) {
        console.error("Error fetching videos:", error);
      }
    };

    fetchVideos();
  }, [userDetails.id]);

  useEffect(() => {
    const fetchFeedback = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/feedback/`);
        const data = await response.json();
        // Filter videos for the logged-in user
        const userFeedback = data.filter((feedback) => feedback.user_id === userDetails.id);
        setFeedback(userFeedback);

        
      } catch (error) {
        console.error("Error fetching videos:", error);
      }
    };

    fetchFeedback();
  }, [userDetails.id]);

  
  
  //const parsedFeedback = JSON.parse(selectedFeedback.feedback);  // Parse feedback string into an array
  //const parsedRecommendations = JSON.parse(selectedFeedback.recommendations);  

  // Fetch feedback for a specific video
  const handleViewFeedback = (videoId) => {
    // Find feedback related to the specific video
    const videoFeedback = feedback.find((item) => item.video_id === videoId);
    setSelectedFeedback(videoFeedback); // Set the selected feedback for the video
    setIsResultsModalOpen(true); // Open the modal
  };

    const handleUpload = async (e) => {
      e.preventDefault();
      if (!videoFile) {
        setUploadStatus('Please select a video to upload.');
        return;
      }
  
      // FormData to send file and metadata
      const formData = new FormData();
      formData.append('title', videoTitle);
      formData.append('video', videoFile);
      formData.append('user_id', userDetails.id);
  
      try {
        setUploadStatus('Uploading...');
        const response = await fetch('http://127.0.0.1:8000/upload_video/', {
          method: 'POST',
          body: formData,
        });
  
        if (response.ok) {
          const data = await response.json();
          setVideoId(data.video_id);
          console.log('Video uploaded successfully:', data);
          setUploadStatus('Upload successful!');
          setIsAnalyzeEnabled(true); // Enable analyze button
        } else {
          console.error('Upload failed:', response.statusText);
          setUploadStatus('Upload failed. Please try again.');
        }
      } catch (error) {
        console.error('Error uploading video:', error);
        setUploadStatus('An error occurred during the upload.');
      }
    };

    // Function to handle the click event for setting the active section
    const handleSectionClick = (section) => {
        setActiveSection(section);
    };

    if (!userDetails) {
        return <p>No user data found. Please log in.</p>;
    }

    const handleAnalyze = async () => {
      if (!videoId) {
        setAnalysisStatus('No video uploaded for analysis.');
        return;
      }
  
      try {
        setAnalysisStatus('Analyzing...');
        const response = await fetch(`http://127.0.0.1:8000/analyze/${videoId}/`, {
          method: 'POST',
          
        });
  
        if (response.ok) {
          const data = await response.json();
          console.log('Analysis result:', data);
          setAnalysisStatus('Analysis completed successfully!');
          setAnalysisResults(data);
          setIsModalOpen(true);

          
          
        } else {
          console.error('Analysis failed:', response.statusText);
          setAnalysisStatus('Analysis failed. Please try again.');
        }
      } catch (error) {
        console.error('Error during analysis:', error);
        setAnalysisStatus('An error occurred during analysis.');
      }
    };

    const getFeedback = (feedbackArray, key) => {
      const item = feedbackArray.find(feedback => Object.keys(feedback)[0] === key);
      return item ? item[key] : 'No feedback available.';
    };
  


    

    return(
        <>
            <div className="flex h-screen">
                {/* Sidebar */}
                <div className="w-64 bg-teal-500 text-white flex flex-col">
                    <a href="#" 
                    className="p-4 hover:bg-teal-600 border-b border-white" 
                    onClick={() => handleSectionClick('Dashboard')}>
                    Dashboard
                    </a>
                    <a href="#" 
                    className="p-4 hover:bg-teal-600 border-b border-white"
                    onClick={() => handleSectionClick('Profile')}>
                    Profile
                    </a>
                    <a href="#" 
                    className="p-4 hover:bg-teal-600 border-b border-white"
                    onClick={() => handleSectionClick('Results')}>
                    My results
                    </a>
                </div>

                {/* Main Content */}
                <div className="flex-1 bg-gray-100 p-6">
                    <h1 className="text-xl font-bold">Main Content</h1>
                    <div className="mt-4">
                    {activeSection === 'Dashboard' && (
                        <div>
                        
                        <div className="container mx-auto p-4">
                    <h1 className="text-2xl font-bold mb-4">Welcome, {userDetails.first_name}! to the Dashboard</h1>
                    <div className="min-h-screen bg-gray-100 text-black flex flex-col items-center p-4">
                      {/* Container */}
                      <div className="w-full max-w-3xl bg-white shadow-md rounded-lg p-6">
                        {/* Top Section */}
                        <div className="flex justify-between mb-6">
                          <div>
                            <h1 className="text-xl font-bold text-blue-600">{userDetails.first_name + userDetails.last_name}</h1>
                            <p className="text-gray-700">{userDetails.profession}</p>
                          </div>
                          <div>
                            <p className="text-gray-700">{userDetails.email}</p>
                          </div>
                        </div>

                        {/* Instruction */}
                        <div className="text-center mb-6">
                          <p className="text-lg text-gray-700">
                            Please upload a video below to get insights on how to improve
                          </p>
                        </div>

                        {/* Upload Form */}
                        <form className="space-y-4" onSubmit={handleUpload}>
                          {/* Title Input */}
                          <div className="flex items-center">
                            <label htmlFor="title" className="text-gray-700 font-semibold mr-2">
                              Title:
                            </label>
                            <input
                              type="text"
                              id="title"
                              className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
                              placeholder="Enter video title"
                              value={videoTitle}
                              onChange={(e) => setVideoTitle(e.target.value)}
                            />
                          </div>

                          {/* File Upload */}
                          <div className="flex items-center">
                            <label
                              htmlFor="videoFile"
                              className="text-gray-700 font-semibold mr-2"
                            >
                              Upload Video:
                            </label>
                            <input
                              type="file"
                              id="videoFile"
                              className="flex-1 px-4 py-2"
                              accept="video/*"
                              onChange={(e) => setVideoFile(e.target.files[0])}
                            />
                          </div>

                          {/* Upload Button */}
                          <button
                            type="submit"
                            className="w-full bg-teal-500 text-white py-2 px-4 rounded-md hover:bg-teal-600 transition"
                          >
                            Submit
                          </button>
                        </form>

                        <div className="mt-2 text-center text-sm text-gray-600">
                          {uploadStatus && <p>{uploadStatus}</p>}
                        </div>

                        {/* Analyze Button */}
                        <div className="mt-6">
                          <button
                            onClick={handleAnalyze}
                            className={`w-full py-2 px-4 rounded-md text-white transition ${
                              isAnalyzeEnabled
                                ? 'bg-orange-500 hover:bg-orange-600'
                                : 'bg-gray-300 cursor-not-allowed'
                            }`}
                            disabled={!isAnalyzeEnabled}
                          >
                            Analyze
                          </button>
                          <div className="mt-2 text-center text-sm text-gray-600">
                            {analysisStatus && <p>{analysisStatus}</p>}
                          </div>
                        </div>

                        {isModalOpen && (
                        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                        <div className="bg-white w-full max-w-2xl rounded-lg shadow-lg p-6">
                          {/* Header */}
                          <div className="mb-4">
                            <h2 className="text-2xl font-bold text-blue-600">
                              Analysis Results for Your Mock Interview Video
                            </h2>
                            <hr className="border-gray-300 mt-2" />
                          </div>

                          {/* Scores Section */}
                          <div className="grid grid-cols-2 gap-4 mb-6">
                            <div className="text-gray-700">
                              <p>Confidence Score: <span className="text-teal-500">{analysisResults?.confidence_score ?? 'N/A'}%</span></p>
                              <p>Clarity Score: <span className="text-teal-500">{analysisResults?.clarity ?? 'N/A'}%</span></p>
                              <p>Average Sentence Length: <span className="text-teal-500">{analysisResults?.avg_sentence_length ?? 'N/A'}</span></p>
                            </div>
                            <div className="text-gray-700">
                              <p>Body Language/Posture: <span className="text-teal-500">{analysisResults?.posture_score ?? 'N/A'}%</span></p>
                              <p>Eye Contact Score: <span className="text-teal-500">{analysisResults?.eye_contact ?? 'N/A'}%</span></p>
                              <p>Number of Filler Words: <span className="text-teal-500">{analysisResults?.filler_word_count ?? 'N/A'}</span></p>
                            </div>
                          </div>

                          {/* Feedback Section */}
                          
                          <div className="mb-6">
                            <h3 className="text-xl font-semibold text-orange-500">Feedback and Recommendations to Improve</h3>
                            <ul className="list-disc list-inside mt-2 text-gray-700">
                              <li>Confidence: {getFeedback(analysisResults.feedback, 'Confidence Score')}</li>
                              <li>Clarity: {getFeedback(analysisResults.feedback, 'Eye Contact Score')}</li>
                              <li>Body Language: {getFeedback(analysisResults.feedback, 'Clarity Score')}</li>
                              <li>Eye Contact: {getFeedback(analysisResults.feedback, 'Body Language/Posture Score')}</li>
                              <li>Average Sentence Length: {getFeedback(analysisResults.feedback, 'Average Sentence Length')}</li>
                              <li>Filler Words: {getFeedback(analysisResults.feedback, 'Filler Words')}</li>
                            </ul>
                          </div>

                          {/* Footer */}
                          <div className="text-right">
                            <button
                              className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-md"
                              onClick={() => setIsModalOpen(false)}
                            >
                              Close
                            </button>
                          </div>
                        </div>
                      </div>
                        )}

                      </div>
                    </div>
                    </div>
                        </div>
                    )}
                    {activeSection === 'Profile' && (
                        <div>
                        <h2 className="text-2xl font-semibold">Your Profile</h2>
                        <p className="text-gray-700 mt-4">Here is the profile content.</p>
                        </div>
                    )}
                    {activeSection === 'Results' && (
                        <div>
                        {/* Results Modal */}
                        {isResultsModalOpen && selectedFeedback && (
                          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                            <div className="bg-white w-full max-w-2xl rounded-lg shadow-lg p-6">
                              {/* Header */}
                              <div className="mb-4">
                                <h2 className="text-2xl font-bold text-blue-600">
                                  Analysis Results for {selectedFeedback.video_title}
                                </h2>
                                <hr className="border-gray-300 mt-2" />
                              </div>
                  
                              {/* Scores Section */}
                              <div className="grid grid-cols-2 gap-4 mb-6">
                                <div className="text-gray-700">
                                  <p>Confidence Score: <span className="text-teal-500">{selectedFeedback.confidence_score}%</span></p>
                                  <p>Clarity Score: <span className="text-teal-500">{selectedFeedback.clarity_score}%</span></p>
                                  <p>Average Sentence Length: <span className="text-teal-500">{selectedFeedback.avd_sentence_length}</span></p>
                                </div>
                                <div className="text-gray-700">
                                  <p>Body Language/Posture: <span className="text-teal-500">{selectedFeedback.body_language_score}%</span></p>
                                  <p>Eye Contact Score: <span className="text-teal-500">{selectedFeedback.eye_contact}%</span></p>
                                  <p>Number of Filler Words: <span className="text-teal-500">{selectedFeedback.filler_word_count}</span></p>
                                </div>
                              </div>
                  
                              {/* Feedback Section */}
                             
                              <div className="mb-6">
                              <h3 className="text-xl font-semibold text-orange-500">
                                Feedback and Recommendations to Improve
                              </h3>
                              <ul className="list-disc list-inside mt-2 text-gray-700">
                                {(Array.isArray(selectedFeedback.recommendations) && selectedFeedback.recommendations.length > 0) ? (
                                  selectedFeedback.recommendations.map((recommendation, index) => (
                                    <li key={index}>{recommendation}</li>
                                  ))
                                ) : (
                                  <li>No recommendations available.</li>
                                )}
                              </ul>
                            </div>
                                                                          
                              {/* Footer */}
                              <div className="text-right">
                                <button
                                  className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-md"
                                  onClick={() => {
                                    setIsResultsModalOpen(false);
                                    setSelectedFeedback(null);
                                  }}
                                >
                                  Close
                                </button>
                              </div>
                            </div>
                          </div>
                        )}
                  
                        {/* Table */}
                        <h2 className="text-2xl font-semibold">My Interview Results</h2>
                        <div className="overflow-x-auto">
                          <table className="min-w-full bg-white border border-gray-300">
                            <thead className="bg-blue-500 text-white">
                              <tr>
                                <th className="py-2 px-4 border">Title</th>
                                <th className="py-2 px-4 border">Video</th>
                                <th className="py-2 px-4 border">Date</th>
                                <th className="py-2 px-4 border">Action</th>
                              </tr>
                            </thead>
                            <tbody>
                              {videos.map((video) => (
                                <tr key={video.id} className="text-center border-b hover:bg-gray-100">
                                  <td className="py-2 px-4">{video.title}</td>
                                  <td className="py-2 px-4">
                                    <a
                                      href={video.video}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="text-blue-500 underline"
                                    >
                                      Watch
                                    </a>
                                  </td>
                                  <td className="py-2 px-4">{new Date(video.date).toLocaleDateString()}</td>
                                  <td className="py-2 px-4 flex justify-center items-center gap-4">
                                    <button
                                      className="bg-teal-500 text-white px-4 py-1 rounded hover:bg-teal-600"
                                      onClick={() => handleViewFeedback(video.id)}
                                    >
                                      View Result
                                    </button>
                                    <button className="text-red-500 hover:text-red-600">
                                      <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        fill="none"
                                        viewBox="0 0 24 24"
                                        strokeWidth={1.5}
                                        stroke="currentColor"
                                        className="w-6 h-6"
                                      >
                                        <path
                                          strokeLinecap="round"
                                          strokeLinejoin="round"
                                          d="M6 18L18 6M6 6l12 12"
                                        />
                                      </svg>
                                    </button>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}
                    </div>
                </div>
                {/* <div className="flex-1 bg-gray-100 p-6">
                    <h1 className="text-xl font-bold">Main Content</h1>
                    <div className="container mx-auto p-4">
                    <h1 className="text-2xl font-bold mb-4">Welcome, {userDetails.first_name}!</h1>
                    <div className="bg-white shadow-md rounded p-6">
                        <p><strong>ID:</strong> {userDetails.id}</p>
                        <p><strong>Email:</strong> {userDetails.email}</p>
                        <p><strong>First Name:</strong> {userDetails.first_name}</p>
                        <p><strong>Last Name:</strong> {userDetails.last_name}</p>
                        <p><strong>Profession:</strong> {userDetails.profession}</p>
                    </div>
                    </div>
                </div> */}
                </div>
        </>
    )
}
export default Dashboard;