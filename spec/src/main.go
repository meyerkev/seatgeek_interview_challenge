package main

import (
	"flag"
	"math/rand"
	"os"
)

func main() {
	servicePort := flag.Int("service-port", 8099, "The port your service exposes to clients")
	numSeats := flag.Int("seats", 500000, "A positive value indicating how many seats to handle")
	concurrencyLevel := flag.Int("concurrency", 150, "A positive value indicating how much concurrency there will be, the higher the more client connections will be attempted. Minimum is 3")
	randomSeed := flag.Int64("seed", 42, "A positive value used to seed the random number generator")
	debugMode := flag.Bool("debug", false, "Prints a lot more detailed logs")

	flag.Parse()
	rand.Seed(*randomSeed)

	logger := NewLogger(*debugMode)

	thereWasAnError := false
	if *concurrencyLevel < NumDifferentClientTypes {
		logger.Errorf("Parameter concurrency must be [%d] or higher, got [%d]", NumDifferentClientTypes, *concurrencyLevel)
		thereWasAnError = true
	}

	if *numSeats < 1 {
		logger.Errorf("Parameter seats must be a positive integer, got [%d]", *numSeats)
		thereWasAnError = true
	}

	if *randomSeed < 1 {
		logger.Errorf("Parameter seed must be a positive integer, got [%d]", *randomSeed)
		thereWasAnError = true
	}

	if *servicePort < 1 {
		logger.Errorf("Parameter service-port must be a positive integer, got [%d]", *servicePort)
		thereWasAnError = true
	}

	if thereWasAnError {
		flag.PrintDefaults()
		os.Exit(1)
	}

	test := NewTester(*servicePort, *numSeats, *concurrencyLevel, logger)

	test.Start()
	test.Run()
	test.Finish()
	os.Exit(0)
}
