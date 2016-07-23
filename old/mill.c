#include <err.h>
#include <errno.h>
#include <popt.h>
#include <readline/readline.h>
#include <readline/history.h>
#include <stdio.h>

#include "libgrbl.h"

int main(int argc, char *argv[])
{
	int rc;
	char *device = "/dev/cnc-mill";
	char *cmdfile = NULL;
	int cmdfd = -1;
	poptContext optcon;
	grblctx *grbl = NULL;

	struct poptOption options[] = {
		{NULL, '\0', POPT_ARG_INTL_DOMAIN, "mill" },
		{"device", 'd', POPT_ARG_STRING, &device, 0,
			"device the mill is attached to", "<device>"},
		{"commands", 'c', POPT_ARG_STRING, &cmdfile, 0,
			"command file", "<cmdfile>"},
		POPT_AUTOALIAS
		POPT_AUTOHELP
		POPT_TABLEEND
	};

	optcon = poptGetContext("mill", argc, (const char **)argv, options, 0);

	rc = poptReadDefaultConfig(optcon, 0);
	if (rc < 0 && !(rc == POPT_ERROR_ERRNO && errno == ENOENT))
		errx(1, "poptReadDefaultConfig failed: %s", poptStrerror(rc));

	while ((rc = poptGetNextOpt(optcon)) > 0)
		;

	if (rc < -1)
		errx(1, "Invalid argument: \"%s\": %s",
		     poptBadOption(optcon, 0), poptStrerror(rc));

	if (poptPeekArg(optcon))
		errx(1, "Invalid argument: \"%s\"",
		     poptPeekArg(optcon));

	if (!device)
		errx(1, "no device specified");

	rc = grbl_new(device, &grbl);
	if (rc < 0)
		err(1, "Couldn't init grbl");

	if (!cmdfile || !strcmp(cmdfile, "-")) {
		cmdfile = NULL;
		cmdfd = STDIN_FILENO;
	} else {
		cmdfd = open(cmdfile, O_RDONLY);
		if (cmdfd < 0)
			err(1, "Couldn't open command file");
	}

	while (1) {
		char *line = NULL;
		if (cmdfd == STDIN_FILENO) {
			line = readline(">");
			if (line && *line) {
				add_history(line);

	}
}
