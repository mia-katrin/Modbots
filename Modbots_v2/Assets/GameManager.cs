using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.SideChannels;
using UnityEngine.SceneManagement;
using System.Collections;
using System;

public class GameManager : MonoBehaviour
{
    // singleton
    private static GameManager instance;
    public static GameManager Instance { get { return instance; } }

    public ComSideChannel pythonCom;

    public static int warmupFixedUpdates = 10;

    public ModularRobot modularRobot;
    public string currentGene = "";
    public bool resetting = false;

    public static int staticIndex = 0;
    public int myIndex = 0;

    public void Awake()
    {
        myIndex = staticIndex;
        //Debug.Log($"I'm GM {myIndex}");
        staticIndex += 1;
        // Make sure there is only one instance of the game manager
        if (instance != null && instance != this)
        {
            //Debug.Log($"GM {myIndex} destroyed");
            //instance.pythonCom.SendMessage($"I am GM {myIndex}, being destroyed");
            this.gameObject.SetActive(false);
            Destroy(this.gameObject);
            return;
        }
        else if (instance == null)
        {
            instance = this;
        }
        DontDestroyOnLoad(gameObject);
        

        // We create the Side Channel
        if (pythonCom == null)
        {
            pythonCom = ComSideChannel.Instance;
            SideChannelsManager.RegisterSideChannel(pythonCom);
        }
        Academy.Instance.OnEnvironmentReset += ResetHappened;
        ComSideChannel.OnReceivedEncoding += NewEncodingGot;
        SceneManager.sceneLoaded += SceneManagerSaysLoaded;

        //Debug.LogError("Done with GM AWake");
    }

    private void Start()
    {
        
    }

    private void SceneManagerSaysLoaded(Scene scene, LoadSceneMode LoadSceneMode)
    {
        //Debug.LogError($"Loaded scene {scene.name}");
        //pythonCom.SendMessage($"Loaded scene {scene.name}");
    }

    private void NewEncodingGot(string gene)
    {
        currentGene = gene;
        //pythonCom.SendMessage("GameManager got encoding");
    }

    private void ResetHappened()
    {
        //pythonCom.SendMessage("GameManager resetting");
        if (resetting)
        {
            return;
        }
        resetting = true;
        if (SceneManager.GetActiveScene().isLoaded)
        {
            //pythonCom.SendMessage("Loading scene");
            SceneManager.LoadScene(0);
        }

        // Make robot
        // every scene load, a modular robot is made (becuse it belongs to the scene)
        // it is responsible for enforcing its singleton-ness itself
        modularRobot.DestroyContents();
        StartCoroutine(CreateRobot());
    }

    public IEnumerator CreateRobot()
    {
        //pythonCom.SendMessage("GameManager starting coroutine");
        Physics.autoSimulation = false;
        for (int i = 0; i < warmupFixedUpdates; i++)
        {
            yield return new WaitForFixedUpdate();
        }
        if (currentGene.Length > 0) modularRobot.MakeRobot(currentGene);
        Physics.autoSimulation = true;

        string indexes = "Created modules: ";
        foreach (GameObject go in modularRobot.allModules)
        {
            indexes += go.GetComponent<ModuleParameterized>().index + ",";
        }
        //pythonCom.SendMessage(indexes);
        resetting = false;
    }

    private void OnDestroy()
    {
        if (Academy.IsInitialized && pythonCom != null)
        {
            SideChannelsManager.UnregisterSideChannel(pythonCom);
        }
    }

    public bool robotElseModule = true;
    private void Update()
    {
        Debug.Log(Application.persistentDataPath);
        if (Input.GetKeyDown(KeyCode.Space))
        {
            if (robotElseModule)
            {
                NewEncodingGot("Random");
                ResetHappened();
            }
            else
            {
                modularRobot.DestroyContents();
                GameObject module = Instantiate(ModularRobot.Instance.modulePrefab);
                ModuleParameterized rootModule = module.GetComponent<ModuleParameterized>();
                rootModule.SetIndex(0);

                rootModule.SetSize(1f);
                rootModule.RemoveFixedJoint();
            }

            modularRobot.MaxStep = 10000000;
        }
    }
}