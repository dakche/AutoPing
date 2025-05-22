<img src="https://github.com/dakche/AutoPing/blob/main/CompanionGUI/psocmemes.png" width="100">
<h1>AutoPing</h1>
<h3>The <i>best</i> AI powered tool to maximize the staffing efficiency of small businesses.</h3>
<h4><i>Featuring the Infineon PSoC 6 AI Evaluation Kit</i></h4><br>
<p>
  Picture this: The customer foot traffic in your small restaurant business is wildly unpredictable. <br><br>
  Sometimes, you might be understaffed to the point where employees are collapsing due to exhaustion. <br>
  Other times, you might have too many cooks in the kitchen and not enough things to do. <br>
  As the owner, you don't want your employees walking out due to overwork nor do you want to pay for staff that really don't need
  to be there. <br><br>
  So what do you do?<br><br>
</p>
<h2>Introducing AutoPing</h2><br>
<p>
  AutoPing constantly monitors the business environment by listening to the ambient noise and uses this information to predict current business conditions. 
  When it infers that there will be a sudden spike in workload in the near future, it will automatically send messages to notify employees on standby to come 
  and help manage the workload, maximizing efficiency for both the workers and the owners, 
  and most of all, saves everyone time and money.<br><br>
  <i>This is an entry in the Hackster.io contest Getting Edgy with Machine Learning. <br>
  More information can be found here: </i>
</p>
<h2>Usage</h2>
<p>
  The repo is divided up into two folders: EdgePing and CompanionGUI.<br><br>
  <strong>EdgePing</strong> contains the ML model and code for the edge device, which consists of the PSoC 6 running an ML algorithm that constantly listens to its environment and estimates the current condition of the business. Once it has determined that the business needs extra assistance, it will send a Serial message to the connected computer that's running CompanionGUI to have it handle the message sending.<br><br>
  <strong>CompanionGUI</strong> contains the code for the user-friendly program + GUI that runs on a computer and connects to the EdgePing module. 
  It is responsible for managing the names of the employees that can be summoned and also receives ML-processed data about the current environment from the EdgePing module. 
  Once the EdgePing module determines that it extra assistance is required, CompanionGUI will send a summon message to employees, notifying them to come to work.

</p>
