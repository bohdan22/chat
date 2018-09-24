import React, { Component } from 'react';
import logo from './logo.svg';
import './base.css';

class App extends Component {
  render() {
    return (
        <nav class="navbar navbar-default">
            <div class="container">
              <div class="navbar-header">
                <a class="navbar-brand" href="">Tornado chat</a>
              </div>
              <div id="navbar">
                <ul class="nav navbar-nav navbar-right">
                  <li><a href="/logout">Logout ({{ user }})</a></li>
                  <li><a href="/channels">Leave room</a></li>
                </ul>
              </div>
            </div>
        </nav>
    );
  }
}

export default App;
