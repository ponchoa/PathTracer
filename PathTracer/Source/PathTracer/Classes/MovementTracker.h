#pragma once

#include "Components/ActorComponent.h"
#include "GameFramework/Actor.h"
#include "MovementTracker.generated.h"

UCLASS()
class PATHTRACER_API UMovementTracker : public UActorComponent
{
	GENERATED_BODY()

public:
	UMovementTracker();

	// Called when the game starts
	virtual void BeginPlay() override;

	// Called every frame
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	/*Allows the Actor path to be tracked*/
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Write Options", DisplayName = "Track Actor Path")
		bool WritePosition;
	/*The time interval (in seconds) between each position check*/
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Write Options", DisplayName = "Time Interval")
		float RefreshTime;

	/*Allows all the tracked paths to be displayed*/
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Read Options", DisplayName = "Display Tracked Path")
		bool ReadPosition;
	/*The time interval (in seconds) between the beginning and the end of the displayed path (if zero or less, the whole path is displayed)*/
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Read Options", DisplayName = "Time Interval")
		float TimeLength;

	FVector ActorPosition;

protected:
	bool VerifyOrCreateDirectory(const FString& TestDir) const;
	bool GetActorWorld();
	void WriteToCurrentFile(FString line);
	TArray<FString> GetCSVFileList();
	bool LoadVectorTimeAndNameFromCSVLine(FString line, FVector& vector, float& time, FString& name);
	void LoadAllVectorsTimesAndNames();
	void DrawDebugPaths();
	void DrawNthPath(size_t n);


	FString DirectoryPath;
	FString FileName;
	bool DirectoryExists;
	bool WorldSet;
	float ElapsedTime;
	float ElapsedTimeSinceLastCheck;
	UWorld *World;

	TArray<TArray<FVector>> VectorList;
	TArray<TArray<float>> TimeList;
	TArray<TArray<FString>> NameList;
	TArray<size_t> PathStartArray;
};