import React from 'react';

interface SidebarProps {
  activeSection: string;
  setActiveSection: (section: string) => void;
  onMakeResume: () => void;
}

// Reorder 'Projects' to be before 'Skills' in this list
const navItems = ['Templates', 'Profile', 'Education', 'Work', 'Projects', 'Skills', 
    'Achievements', 
    'Certifications'];

const Sidebar: React.FC<SidebarProps> = ({ activeSection, setActiveSection, onMakeResume }) => {
  return (
    <>
      <ul className="nav-list">
        {navItems.map(item => (
          <li
            key={item}
            className={`nav-item ${activeSection === item ? 'active' : ''}`}
            onClick={() => setActiveSection(item)}
          >
            {item}
          </li>
        ))}
      </ul>
      <button className="btn btn-primary make-button" onClick={onMakeResume}>
        MAKE
      </button>
    </>
  );
};

export default Sidebar;