<h1 align="center">
  <b><i>Compressore</i></b>
  <br>
</h1>

<h4 align="center">A simple script to backup multiple directories and send them via ssh.</h4>

<p align="center">
  <img alt="GitHub" src="https://img.shields.io/github/license/Ravazziniandrea/compressore">
  <!--<a href="https://www.codefactor.io/repository/github/ravazziniandrea/compressore"><img src="https://www.codefactor.io/repository/github/ravazziniandrea/compressore/badge" alt="CodeFactor" /></a>-->
</p>

<p align="center">
  <a href="#how">How to Use</a> -
  <a href="#dependencies">Dependencies</a> -
  <a href="#problems">Problems</a> -
  <a href="#credits">Credits</a>
</p>

<h3 id="how"><i>How to Use</i></h3>
<p>  
  To get started, you have to edit params.json:
  <ul>
    <li><b>folder_to_backup:</b> list of folders to backup</li>
    <li><b>tmp_store_folder:</b> folder to store the temporarily the backup on the local pc</li>
    <li><b>ssh</b>
        <ul>
          <li><b>enable:</b> 1/0 to enable/disable the ssh copy. If it's 0, the other parameters in ssh can be left empty ""</li>
          <li><b>ip: </b> ip address to the machine connected via ssh</li>
          <li><b>port: </b> ssh port (22 is the default)</li>
          <li><b>user:</b> user used to connect via ssh</li>
          <li><b>folder:</b> folder in which the backup is stored once sended</li>
        </ul>
    </li>
    <li><b>log</b>
      <ul>
        <li><b>enable:</b> 1/0 to enable/disable the logging to file. If it's 0, the other parameters in log can be left empty ""</li>
        <li><b>folder:</b> path to the folder in which it's written the .log file</li>
      </ul>
    </li>
  </ul>
  
  after you have modified the parameters, simply launch compressore.py:
  ```bash
  $ python compressore.py
  ```
</p>
<br>

<h3 id="dependencies"><i>Dependencies</i></h3> 
<p>  
    <ul>
    <li><b>Systems:</b></li>
      <ul>
        <li>Linux</li>
        <li>Mac Os</li>
      </ul>
      <li><b>Packages:</b></li>
      <ul>
        <li>python >= 3.0</li>
        <li>tar</li>
        <li>pbzip2</li>
        <li>sshpass</li>
        <li>scp</li>
      </ul>
  </ul>
</p>
<br>

<h3 id="problems"><i>Problems</i></h3>
<p>
  <ul>
    <li>The logging to file still doesn't work with shell commands.</li>
    <li>Right now this project works only on *nix systems. I'm currently developing a solution to make it work on Windows. </li>
    <li>It's not the best python code you have ever seen, I apologize for that but I have a strong Java background 🤷, I will make it more "python friendly".</li>
  </ul>  
  For any help, your pr are VERY apriciated! Thanks!
</p>
<br>

<h3 id="credits"><i>Credits</i></h3>
<p>  
  <a href="https://www.linkedin.com/in/andrea-ravazzini/">
    <img src="https://brand.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg">
  </a>
</p>
