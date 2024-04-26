import React from 'react';
import { Navbar, Nav, Container} from 'react-bootstrap';
import'';
const Header =() => {
  const Logout =()=>{

  }
  return (
    <>
      <Navbar bg="dark" variant="dark" className='header'>
        <Container>
          <Navbar.Brand href="../pages/Dashboard/Dashboard.js">Bus Booking</Navbar.Brand>

          <Nav className="ms-auto">
          </Nav>
        </Container>
      </Navbar>
    </>
  );
}

export default Header;