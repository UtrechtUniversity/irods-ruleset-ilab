testRule {
	iiGrantReadAccessToResearchGroup(*path, *status, *statusInfo);
	writeLine("stdout", *status);
	writeLine("stdout", *statusInfo);
}
input *path=""
output ruleExecOut
