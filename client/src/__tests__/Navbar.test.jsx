import { render, screen } from '@testing-library/react';
import Navbar from '../components/Navbar';
test('renders logo', () => {
  render(<Navbar />);
  expect(screen.getByText(/Public Pulse/i)).toBeInTheDocument();
}); 