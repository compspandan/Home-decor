import {BrowserRouter as Router, Route, Routes as Switch} from "react-router-dom";
import {Login} from "./components/Login";
import AddProjectForm from "./components/projectManager/AddProjectForm";
import ProjectDetails from "./components/projectManager/ProjectDetails";
import ProjectList from "./components/projectManager/ProjectList";
import ProjectListDes from "./components/designer/ProjectList";
import { SignUp } from "./components/SignUp";
import DesignerProjectDetails from "./components/designer/DesignerProjectDetails";
export default function Routes()
{
	return (
		<Router>
			<Switch>
				<Route path='/' element={<Login/>}/>
				<Route path='/signup' element={<SignUp/>}/>
				<Route path='/projectManager' element={<ProjectList/>}/>
				<Route path='/designer' element={<ProjectListDes/>}/>
				<Route path='/projectManager/:projectId' element={<ProjectDetails/>}/>
				<Route path='/designer/:projectId' element={<DesignerProjectDetails/>}/>
				<Route path='/addproject' element={<AddProjectForm/>}/>
			</Switch>
		</Router>
	);
}