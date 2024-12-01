import {Outlet, Link} from "react-router-dom";
import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function Layout() {
    const navigate = useNavigate();

    const [isModalOpen, setIsModalOpen] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [activeModal, setActiveModal] = useState(null);

    const [formData, setFormData] = useState({
        email: '',
        first_name: '',
        last_name: '',
        profession: '',
        password: '',
        confirmPassword: '',
      });
      const [error, setError] = useState('');
      const [successMessage, setSuccessMessage] = useState('');

      const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
      const [loginFormData, setLoginFormData] = useState({
        email: '',
        password: '',
      });
      const [loginError, setLoginError] = useState('');
      const [loginSuccessMessage, setLoginSuccessMessage] = useState('');
  

      const toggleModal = () => {
        setIsModalOpen(!isModalOpen);
        setError('');
        setSuccessMessage('');
        setFormData({
          email: '',
          first_name: '',
          last_name: '',
          profession: '',
          password: '',
          confirmPassword: '',
        });
      };

      const handleChange = (e) => {
        setFormData({
          ...formData,
          [e.target.name]: e.target.value,
        });
      };

      const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccessMessage('');
    
        // Validate password match
        if (formData.password !== formData.confirmPassword) {
          setError('Passwords do not match!');
          return;
        }
    
        try {
          const response = await axios.post('http://127.0.0.1:8000/register/', {
            email: formData.email,
            first_name: formData.first_name,
            last_name: formData.last_name,
            profession: formData.profession,
            password: formData.password,
          });
    
          if (response.status === 201) {
            const { token } = response.data;
            localStorage.setItem('access_token', token.access);
            localStorage.setItem('refresh_token', token.refresh);
            // Store user details
            const user_response = await axios.get('http://127.0.0.1:8000/user-details/', {
              headers: {
                Authorization: `Bearer ${localStorage.getItem('access_token')}`,
              },
            });
            const userDetails = user_response.data;
            localStorage.setItem('user_details', JSON.stringify(userDetails));
            setSuccessMessage('Registration successful!');
            setTimeout(() => {
              toggleModal();
            }, 2000); // Close modal after success
            navigate('/Dashboard');
          }
        } catch (err) {
          setError(
            err.response?.data?.message || 'An error occurred during registration!'
          );
        }
      };

    
      const toggleLoginModal = () => {
        setIsLoginModalOpen(!isLoginModalOpen);
        setLoginError('');
        setLoginSuccessMessage('');
        setLoginFormData({
          email: '',
          password: '',
        });
      };
    
      const handleLoginChange = (e) => {
        setLoginFormData({
          ...loginFormData,
          [e.target.name]: e.target.value,
        });
      };
    
      const handleLoginSubmit = async (e) => {
        e.preventDefault();
        setLoginError('');
        setLoginSuccessMessage('');
    
        try {
          const response = await axios.post('http://127.0.0.1:8000/login/', {
            email: loginFormData.email,
            password: loginFormData.password,
          });
    
          if (response.status === 200) {
            // Store the JWT token 
            localStorage.setItem('access_token', response.data.access);
            localStorage.setItem('refresh_token', response.data.refresh);
            // Store user details
            const user_response = await axios.get('http://127.0.0.1:8000/user-details/', {
              headers: {
                Authorization: `Bearer ${localStorage.getItem('access_token')}`,
              },
            });
            const userDetails = user_response.data;
            localStorage.setItem('user_details', JSON.stringify(userDetails));
            // Set the default authorization header
            axios.defaults.headers['Authorization'] = `Bearer ${response.data.access}`;
            setLoginSuccessMessage('Login successful!');
            setTimeout(() => {
              toggleLoginModal();
            }, 2000); // Close modal after success
            navigate('/Dashboard')
          }
        } catch (err) {
          setLoginError(
            err.response?.data?.message || 'An error occurred during login!'
          );
          console.log(err);
        }
      };
    

    const togglePasswordVisibility = () => {
        setShowPassword(!showPassword);
      };
    
      const toggleConfirmPasswordVisibility = () => {
        setShowConfirmPassword(!showConfirmPassword);
      };

    return(
        <>
        <nav className="bg-blue-400 text-white shadow-md">
            <div className="container mx-auto px-4 py-3 flex justify-between items-center">
                {/* Logo */}
                <div className="text-2xl font-bold">MockSmart</div>

                {/* Navigation Links */}
                <div className="flex items-center space-x-6">
                <a href="/" className="hover:text-teal-200 transition">Home</a>
                <a href="/About" className="hover:text-teal-200 transition">About Us</a>
                <a href="/Contacts" className="hover:text-teal-200 transition">Contact Us</a>

                {/* Buttons */}
                <button onClick={toggleLoginModal} className="bg-teal-500 hover:bg-teal-600 text-white px-4 py-2 rounded-md transition">
                    Login
                </button>
                <button  onClick={toggleModal} className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-md transition">
                    Register
                </button>
                </div>
            </div>
            </nav>

            {/* Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div className="bg-white rounded-lg w-full max-w-md p-6">
                    <h2 className="text-2xl font-bold text-blue-500 mb-4">Register</h2>
                    <form onSubmit={handleSubmit}>
                    {error && (
                        <p className="text-red-500 text-sm mb-4">{error}</p>
                    )}
                    {successMessage && (
                        <p className="text-green-500 text-sm mb-4">{successMessage}</p>
                    )}
                    {/* Email */}
                    <div className="mb-4">
                        <label className="block text-gray-700">Email</label>
                        <input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                        />
                    </div>

                    {/* First Name */}
                    <div className="mb-4">
                        <label className="block text-gray-700">First Name</label>
                        <input
                        type="text"
                        name="first_name"
                        value={formData.first_name}
                        onChange={handleChange}
                        className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                        />
                    </div>

                    {/* Last Name */}
                    <div className="mb-4">
                        <label className="block text-gray-700">Last Name</label>
                        <input
                        type="text"
                        name="last_name"
                        value={formData.last_name}
                        onChange={handleChange}
                        className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                        />
                    </div>

                    {/* Profession */}
                    <div className="mb-4">
                        <label className="block text-gray-700">Profession</label>
                        <input
                        type="text"
                        name="profession"
                        value={formData.profession}
                        onChange={handleChange}
                        className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                        />
                    </div>

                    {/* Password */}
                    <div className="mb-4">
                        <label className="block text-gray-700">Password</label>
                        <div className="relative">
                        <input
                            type={showPassword ? "text" : "password"}
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            required
                        />
                        <button
                            type="button"
                            onClick={togglePasswordVisibility}
                            className="absolute inset-y-0 right-3 flex items-center text-blue-500 hover:text-blue-600"
                        >
                            {showPassword ? "Hide" : "Show"}
                        </button>
                        </div>
                    </div>


                    {/* Confirm Password */}
                    <div className="mb-4">
                        <label className="block text-gray-700">Confirm Password</label>
                        <div className="relative">
                        <input
                            type={showConfirmPassword ? "text" : "password"}
                            name="confirmPassword"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            required
                        />
                        <button
                            type="button"
                            onClick={toggleConfirmPasswordVisibility}
                            className="absolute inset-y-0 right-3 flex items-center text-blue-500 hover:text-blue-600"
                        >
                            {showConfirmPassword ? "Hide" : "Show"}
                        </button>
                        </div>
                    </div>

                    {/* Submit Button */}
                    <div className="flex justify-between items-center">
                        <button
                        type="button"
                        onClick={toggleModal}
                        className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-md transition"
                        >
                        Cancel
                        </button>
                        <button
                        type="submit"
                        className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md transition"
                        >
                        Register
                        </button>
                    </div>
                    </form>
                </div>
                </div>
            )}

            {/* Login Modal */}
            {isLoginModalOpen && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div className="bg-white rounded-lg w-full max-w-md p-6">
                    <h2 className="text-2xl font-bold text-blue-500 mb-4">Login</h2>
                    <form onSubmit={handleLoginSubmit}>
                    {loginError && (
                        <p className="text-red-500 text-sm mb-4">{loginError}</p>
                    )}
                    {loginSuccessMessage && (
                        <p className="text-green-500 text-sm mb-4">{loginSuccessMessage}</p>
                    )}
                    <div className="mb-4">
                        <label className="block text-gray-700">Email</label>
                        <input
                        type="email"
                        name="email"
                        value={loginFormData.email}
                        onChange={handleLoginChange}
                        className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                        />
                    </div>
                    <div className="mb-4 relative">
                        <label className="block text-gray-700">Password</label>
                        <input
                            type={showPassword ? "text" : "password"}
                            name="password"
                            value={loginFormData.password}
                            onChange={handleLoginChange}
                            className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            required
                        />
                        <button
                            type="button"
                            onClick={togglePasswordVisibility}
                            className="absolute inset-y-0 right-3 flex items-center text-blue-500 hover:text-blue-600"
                        >
                            {showPassword ? "Hide" : "Show"}
                        </button>
                    </div>
                    <div className="flex justify-between items-center">
                        <button
                        type="button"
                        onClick={toggleLoginModal}
                        className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-md transition"
                        >
                        Cancel
                        </button>
                        <button
                        type="submit"
                        className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md transition"
                        >
                        Login
                        </button>
                    </div>
                    </form>
                </div>
                </div>
            )}

        <Outlet />

        {/* Footer */}
      <footer className="bg-gray-800 text-white text-center py-4">
        <p>© 2024 MockSmart. All Rights Reserved.</p>
      </footer>
        
        </>
    )
}
export default Layout;