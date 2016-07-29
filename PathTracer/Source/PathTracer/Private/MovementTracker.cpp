#include "PathTracerPrivatePCH.h"
#include "MovementTracker.h"

UMovementTracker::UMovementTracker()
{
	//Default values, accessible from the editor
	WritePosition = false;
	ReadPosition = false;
	RefreshTime = 0.01f;
	TimeLength = 1.0f;

	//Other values used in this Plugin
	WorldSet = false;
	ElapsedTime = 0.0f;
	ElapsedTimeSinceLastCheck = 0.0f;
	bWantsBeginPlay = true;
	PrimaryComponentTick.bCanEverTick = true;
	DirectoryPath = FString(FPaths::GameDir() + "/Data/MovementTracker");
	FPaths::NormalizeDirectoryName(DirectoryPath);
	FileName = DirectoryPath + "/" + FDateTime().Now().ToString() + ".csv";
	DirectoryExists = VerifyOrCreateDirectory(DirectoryPath);
	PathStartArray = TArray<size_t>();

	//The lists of lists: Each list contained in these lists corresponds to one CSV file, one path, and are all in the same position.
	VectorList = TArray<TArray<FVector>>();
	TimeList = TArray<TArray<float>>();
	NameList = TArray<TArray<FString>>();
}

/// <summary> Writes a full line at the end of the file created for this session </summary>
/// <param name="line"> The text line to append at the end of the file </param>
void UMovementTracker::WriteToCurrentFile(FString line)
{
	if (WritePosition && DirectoryExists)
	{
		IPlatformFile& PlatformFile = FPlatformFileManager::Get().GetPlatformFile();
		IFileHandle* handle = PlatformFile.OpenWrite(*FileName, true);
		if (handle)
		{
			handle->Write((const uint8 *)TCHAR_TO_ANSI(*line), line.Len());
			handle->Write((const uint8 *)"\n", 1);
			delete handle;
		}
	}
}

/// <summary> Lists all the CSV files contained in the Data/MovementTracker directory </summary>
/// <returns> A list of all the paths pointing to the files in the Data/MovementTracker directory </returns>
TArray<FString> UMovementTracker::GetCSVFileList()
{
	TArray<FString> files = TArray<FString>();

	if (DirectoryExists)
	{
		IFileManager& FileManager = IFileManager::Get();
		FString FinalPath = DirectoryPath + "/*.csv";

		FileManager.FindFiles(files, *FinalPath, true, false);
		for (size_t i = 0; i < files.Num(); i++)
		{
			files[i] = DirectoryPath + "/" + files[i];
		}
	}
	return files;
}

// Called when the game starts
void UMovementTracker::BeginPlay()
{
	Super::BeginPlay();
	ActorPosition = GetOwner()->GetActorLocation();

	//If the tracker is on, it will put the labels at the beginning of the CSV file:
	WriteToCurrentFile(FString("X,Y,Z,time,date,actor name"));
	if (ReadPosition && DirectoryExists)
		LoadAllVectorsTimesAndNames();
}

/// <summary> Fills the lists of lists that contain, in the corresponding order, all of the positions, time and actor names recorded </summary>
void UMovementTracker::LoadAllVectorsTimesAndNames()
{
	TArray<FString> files = GetCSVFileList();
	for (size_t i = 0; i < files.Num(); i++)
	{
		//Initializing the lists representing one path or one CSV file
		TArray<FVector> VList = TArray<FVector>();
		TArray<float> TList = TArray<float>();
		TArray<FString> NList = TArray<FString>();
		TArray<FString> lines = TArray<FString>();

		if (FFileHelper::LoadANSITextFileToStrings(*files[i], NULL, lines))
		{
			FVector Vector;
			float Time;
			FString Name = "";
			for (size_t y = 0; y < lines.Num() - 1; y++)
			{
				//Sets the Position, Time and Actor Name values
				if (LoadVectorTimeAndNameFromCSVLine(lines[y], Vector, Time, Name))
				{
					VList.Add(Vector);
					TList.Add(Time);
					NList.Add(Name);
				}
			}
			VectorList.Add(VList);
			TimeList.Add(TList);
			NameList.Add(NList);
			PathStartArray.Add(0);
		}
	}
}

/// <summary> Parse a line from a CSV file and sets the values accordingly </summary>
/// <param name="line"> The line from a CSV file to analyse </param>
/// <param name="vector"> The Position to be set </param>
/// <param name="time"> The Time to be set </param>
/// <param name="name"> The Actor Name to be set </param>
/// <returns> True if it succeeded and false if not </returns>
bool UMovementTracker::LoadVectorTimeAndNameFromCSVLine(FString line, FVector& vector, float& time, FString& name)
{
	TArray<FString> Parsed;
	line.ParseIntoArray(Parsed, TEXT(","), false);

	//Removes unnecessary whitespaces at the beginnings and ends of each comma-separated value
	for (size_t i = 0; i < Parsed.Num(); i++)
	{
		Parsed[i].Shrink();
		Parsed[i].Trim();
	}

	//If the actor name value exists
	if (Parsed.Num() >= 6)
		name = Parsed[5];
	//If the X, Y, Z and time values exist
	if (Parsed.Num() >= 4 && Parsed[0].IsNumeric() && Parsed[1].IsNumeric() && Parsed[2].IsNumeric() && Parsed[3].IsNumeric())
	{
		vector.X = FCString::Atof(*Parsed[0]);
		vector.Y = FCString::Atof(*Parsed[1]);
		vector.Z = FCString::Atof(*Parsed[2]);
		time = FCString::Atof(*Parsed[3]);

		return true;
	}

	return false;
}

// Called every frame
void UMovementTracker::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	ElapsedTime += DeltaTime;
	ElapsedTimeSinceLastCheck += DeltaTime;

	//If the time between two recording was reached
	if (ElapsedTimeSinceLastCheck >= RefreshTime)
	{
		//Writes the comma-seprated values that are obeserved
		if (WritePosition)
		{
			ActorPosition = GetOwner()->GetActorLocation();
			FString line = FString::SanitizeFloat(ActorPosition.X) + "," +
				FString::SanitizeFloat(ActorPosition.Y) + "," +
				FString::SanitizeFloat(ActorPosition.Z) + "," +
				FString::SanitizeFloat(ElapsedTime) + "," +
				FString::FromInt((int)FDateTime().Now().ToUnixTimestamp()) + "," +
				GetOwner()->GetName();
			WriteToCurrentFile(line);
		}
		ElapsedTimeSinceLastCheck = 0.0f;
	}
	//Tries to get the world containing the actor until it succeeds
	if (!WorldSet)
		WorldSet = GetActorWorld();
	//Draws the paths
	if (WorldSet && ReadPosition)
		DrawDebugPaths();
}

/// <summary> Verifies if the directory exists, and creates it if not </summary>
/// <param name="TestDir"> The full path of the directory to check </param>
/// <returns> True if the directory existed or was created, false if it couldn't find or create it </returns>
bool UMovementTracker::VerifyOrCreateDirectory(const FString& TestDir) const
{
	IPlatformFile& PlatformFile = FPlatformFileManager::Get().GetPlatformFile();

	return (PlatformFile.CreateDirectoryTree(*TestDir));
}

/// <summary> Sets the world value the Actor is in </summary>
/// <returns> True if the world was found, false if it was not loaded yet </returns>
bool UMovementTracker::GetActorWorld()
{
	World = GetOwner()->GetWorld();
	return World != NULL;
}

/// <summary> Draws all of the paths using the lists of lists containing all relevant information (position, time and actor name) </summary>
void UMovementTracker::DrawDebugPaths()
{
	//Checks if there is no mistake in the different lists
	if (WorldSet && ReadPosition && VectorList.Num() == TimeList.Num() && NameList.Num() == TimeList.Num())
	{
		for (size_t i = 0; i < VectorList.Num(); i++)
		{
			//Since each list contained in the three lists of lists represent the same path as the other ones at the same position,
			//only one value needs to be used for all three lists
			DrawNthPath(i);
		}
	}
}

/// <summary> Draws one of the paths using one list from each list of lists </summary>
/// <param name="n"> The position, in each list of lists, of the list with the values for this path </param>
void UMovementTracker::DrawNthPath(size_t n)
{
	//Checks if there is no mistake in the different lists
	if (VectorList[n].Num() == TimeList[n].Num() && TimeList[n].Num() == NameList[n].Num())
	{
		//previous tells us if the previous point was drawn. It allows us to know if a line needs to be drawn between the points
		//but also tells us when the path's beginning was. It allows us to start at that point next update to save on resources.
		bool previous = false;
		for (size_t i = PathStartArray[n]; i < VectorList[n].Num(); i++)
		{
			if ((TimeLength <= 0 || TimeList[n][i] >= ElapsedTime - TimeLength) && TimeList[n][i] <= ElapsedTime && NameList[n][i] == GetOwner()->GetName())
			{
				DrawDebugPoint(World, VectorList[n][i], 20.0f, FColor(255, 0, 0));
				if (previous) //Draw the line between the previous point and this one
					DrawDebugLine(World, VectorList[n][i - 1], VectorList[n][i], FColor(0, 0, 255), false, -1.0f, (uint8)'\000', 5.0f);
				else //Sets the start of next update's sweep
					PathStartArray[n] = i;
				previous = true;
			}
			else
			{
				previous = false;
				if (previous) //We are at the end of the path that we want to draw, no need to continue checking the rest of the path
					break;
			}
		}
	}
}