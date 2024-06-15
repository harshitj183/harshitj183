
  //<script src="https://cdn.githubraw.com/harshitj183/harshitj183/main/badge/floating.js" </script>
// fetch('https://cdn.jsdelivr.net/gh/harshitj183/harshitj183@main/badge/floating.js')
//  .then(response => response.text())
//  .then(script => eval(script));
  
  // Create the badge element
  const badge = document.createElement('div');
  badge.id = 'badge_843219';
  badge.className = 'badge_219843';

  // Create the logo element
  const logo = document.createElement('img');
  logo.id = 'logo_982134';
  logo.className = 'logo_412983';
  logo.src = 'https://cdn.githubraw.com/harshitj183/harshitj183/main/badge/profileLOgo.png';
  logo.alt = 'Google logo';

  // Create the text element
  const text = document.createElement('div');
  text.id = 'text_654321';
  text.className = 'text_123654';

  // Create the partner element
  const partner = document.createElement('span');
  partner.id = 'partner_765432';
  partner.className = 'partner_345678';
  partner.textContent = '@harshitj183';

  // Create the fullName element
  const fullName = document.createElement('span');
  fullName.id = 'fullName_987654';
  fullName.className = 'full-name_567890';
  fullName.textContent = 'Harshit Jaiswal';

  // Create the developedByText element
  const developedByText = document.createElement('span');
  developedByText.id = 'developedByText_456789';
  developedByText.className = 'developed-by-text_890123';
  developedByText.textContent = 'Developed by';

  // Append the elements to the page
  text.appendChild(developedByText);
  text.appendChild(partner);
  text.appendChild(fullName);
  badge.appendChild(logo);
  badge.appendChild(text);
  document.body.appendChild(badge);

  // Add the CSS styles
  const styles = `
  #badge_843219 {
      position: fixed;
      bottom: 10px;
      right: 10px;
      display: flex;
      align-items: center;
      padding: 2px;
      background-color: #4285f4;
      border: 1px solid #4285f4;
      border-radius: 3px;
      font-size: 10px;
      color: #fff;
      width: 150px;
      height: 30px;
      animation: trending 2s infinite;
    }

  #logo_982134 {
      position: absolute;
      top: -10px;
      left: -10px;
      width: 50px;
      height: 50px;
      border-radius: 25%;
      border: 2px solid #fff;
      border-bottom: 2px solid #4285f4;
      border-radius: 50% 50% 50% 50%/60% 60% 40% 40%;
    }

  #text_654321 {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      margin-left: 50px;
    }

  #partner_765432 {
      color: #fff;
      font-weight: bold;
      display: block;
    }

  #fullName_987654 {
      display: none;
    }

    @keyframes trending {
      0% {
        transform: scale(1);
      }
      50% {
        transform: scale(1.1);
      }
      100% {
        transform: scale(1);
      }
    }
  `;

  const styleSheet = document.createElement('style');
  styleSheet.textContent = styles;
  document.head.appendChild(styleSheet);

  // Add hover effect to badge
  badge.addEventListener('mouseover', () => {
    developedByText.style.display = 'none';
    fullName.style.display = 'block';
  });

  badge.addEventListener('mouseout', () => {
    developedByText.style.display = 'block';
    fullName.style.display = 'none';
  });
 
